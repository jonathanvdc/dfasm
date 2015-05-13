import Instructions
import Assembler
import Lexer
from Encoding import *

precedence = {
    "asterisk" : 0,
    "slash" : 0,
    "percent" : 0,
    "plus" : 1,
    "minus" : 1,
    "lessthanlessthan" : 2,
    "greaterthangreaterthan" : 2,
    "and" : 3,
    "or" : 4
}

operations = {
    "plus"                   : lambda lhs, rhs: lhs + rhs,
    "minus"                  : lambda lhs, rhs: lhs - rhs,
    "asterisk"               : lambda lhs, rhs: lhs * rhs,
    "slash"                  : lambda lhs, rhs: lhs / rhs,
    "percent"                : lambda lhs, rhs: lhs % rhs,
    "and"                    : lambda lhs, rhs: lhs & rhs,
    "or"                     : lambda lhs, rhs: lhs | rhs,
    "lessthanlessthan"       : lambda lhs, rhs: lhs << rhs,
    "greaterthangreaterthan" : lambda lhs, rhs: lhs >> rhs
}

class TokenStream(object):
    """ Defines a token stream. """ 
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        """ Peeks a token from the token stream. """
        if self.index >= len(self.tokens):
            return Lexer.Token("", "end-of-stream")
        return self.tokens[self.index]

    def peekNoTrivia(self):
        """ Peeks a non-trivia token from the token stream. """
        result = self.peek()
        i = 1
        while result.isTrivia():
            if self.index + i >= len(self.tokens):
                return Lexer.Token("", "end-of-stream")
            result = self.tokens[self.index + i]
            i += 1
        return result

    def isEmpty(self):
        """ Finds out if the token stream is empty. """
        return self.index >= len(self.tokens)

    def isTrivia(self):
        """ Finds out if all future tokens in the token stream are trivia. """
        return self.isEmpty() or all([item.isTrivia() for item in self.tokens[self.index:]])

    def nextToken(self):
        """ Reads the next token from the token stream. """
        if self.index >= len(self.tokens):
            return Lexer.Token("", "end-of-stream")
        i = self.index
        self.index += 1
        return self.tokens[i]

    def skipTrivia(self):
        """ Skips trivia tokens. """
        while self.peek().isTrivia():
            self.nextToken()

    def nextNoTrivia(self):
        """ Reads the next non-trivia token. """
        self.skipTrivia()
        return self.nextToken()
            

class LiteralNode(object):
    """ Describes a literal syntax node. """
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return str(self.token)

class IntegerNode(LiteralNode):
    """ Describes an integer syntax node. """

    def toOperand(self, asm):
        """ Converts the integer node to an operand. """
        val = int(self.token.contents)
        if -128 <= val <= 127:
            return Instructions.ImmediateOperand(val, to8, 1)
        elif -2 ** 16 <= val <= 2 ** 16 - 1:
            return Instructions.ImmediateOperand(val, to16le, 4)
        else:
            return Instructions.ImmediateOperand(val, to32le, 4)

    def __repr__(self):
        return "IntegerNode(%r)" % self.token

class IdentifierNode(LiteralNode):
    """ Describes an identifier syntax node. """

    def toOperand(self, asm):
        """ Converts the identifier node to an operand. """
        name = self.token.contents
        if name in Instructions.registers: # Maybe we'll get lucky and encounter a register.
            return Instructions.RegisterOperand(Instructions.registers[name])
        else:
            return Instructions.ImmediateOperand.createUnsigned(asm.labels[name])


    def __repr__(self):
        return "IdentifierNode(%r)" % self.token

class BinaryNode(object):
    """ Defines a syntax node that captures a binary expression. """
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def toOperand(self, asm):
        """ Converts the binary node to an operand, trying to constant-fold in the process. """
        lhs = self.left.toOperand(asm)
        rhs = self.right.toOperand(asm)
        if isinstance(lhs, Instructions.ImmediateOperand) and isinstance(rhs, Instructions.ImmediateOperand):
            return Instructions.ImmediateOperand.createSigned(operations[self.op](lhs.value, rhs.value))
        else:
            return Instructions.BinaryOperand(lhs, rhs) # Create a binary pseudo-operand (which MemoryNode can then examine)

    def __str__(self):
        return str(self.left) + " " + str(self.op) + " " + str(self.right)

    def __repr__(self):
        return "BinaryNode(%r, %r, %r)" % (self.left, self.op, self.right)

class MemoryNode(object):
    """ Defines a syntax node that refers to a memory location. """
    def __init__(self, lbracket, address, rbracket):
        self.lbracket = lbracket
        self.address = address
        self.rbracket = rbracket

    def __str__(self):
        return str(self.lbracket) + str(self.address) + str(self.rbracket)

    def __repr__(self):
        return "MemoryNode(%r, %r, %r)" % (self.lbracket, self.address, self.rbracket)

class SeparatedNode(object):
    """ Describes a syntax node that may be prefixed by a separator token. """
    def __init__(self, separator, node):
        self.separator = separator
        self.node = node

    def toOperand(self, asm):
        return self.node.toOperand(asm)

    def __str__(self):
        if self.separator is not None:
            return str(self.separator) + " " + str(self.node)
        else:
            return str(self.node)

    def __repr__(self):
        return "SeparatedNode(%r, %r)" % (self.separator, self.node)

class SeparatedList(object):
    """ Defines a list of separated syntax nodes. """
    def __init__(self, nodes):
        self.nodes = nodes

    def __iter__(self):
        return iter(map(lambda x: x.node, self.nodes))

    def toOperands(self, asm):
        return map(lambda x: x.toOperand(asm), self.nodes)

    def __str__(self):
        return "".join(map(str, self.nodes))

    def __repr__(self):
        return "SeparatedList(%r)" % self.nodes

class InstructionNode(object):
    """ Describes an instruction syntax node. """
    def __init__(self, mnemonic, argumentList):
        self.mnemonic = mnemonic
        self.argumentList = argumentList

    def __str__(self):
        return str(self.mnemonic) + " " + str(self.argumentList)

    def __repr__(self):
        return "InstructionNode(%r, %r)" % (self.mnemonic, self.argumentList)

class ParenthesesNode(object):
    """ Represents a parenthesized syntax node. """
    def __init__(self, lparen, expr, rparen):
        self.lparen = lparen
        self.expr = expr
        self.rparen = rparen

    def toOperand(self, asm):
        """ Converts the parenthesized node to an operand. """
        return self.expr.toOperand(asm)

    def __str__(self):
        return str(self.lparen) + str(self.expr) + str(self.rparen)

    def __repr__(self):
        return "ParenthesesNode(%r, %r, %r)" % (self.lparen, self.expr, self.rparen)

class LabelNode(object):
    """ Describes a label syntax node. """
    def __init__(self, name, colon):
        self.name = name
        self.colon = colon

    def __str__(self):
        return str(self.name) + str(self.colon)

    def __repr__(self):
        return "LabelNode(%r, %r)" % (self.name, self.colon)

def parseArgument(tokens):
    """ Parse an argument to an instruction:

        mov  ax, [bx+si]
             ^~  ^~~~~~~
    """
    peek = tokens.peekNoTrivia()
    if peek.type == "lbracket":
        return parseMemory(tokens)
    else:
        left = parsePrimary(tokens)
        return parseBinary(tokens, left, 10000)

def parseArgumentList(tokens):
    """ Parse an instruction's argument list:

        mov  ax, [bx+si]
             ^~~~~~~~~~~
    """
    results = []
    while not tokens.isTrivia():
        if len(results) == 0:
            sep = None
        elif tokens.peekNoTrivia().type == "comma":
            sep = tokens.nextNoTrivia()
        else:
            return SeparatedList(results)

        node = parseArgument(tokens)
        results.append(SeparatedNode(sep, node))

    return SeparatedList(results)

def parseMemory(tokens):
    """ Parse a memory location in brackets:

        mov  ax, [bx+si]
                 ^~~~~~~
    """
    lbracket = tokens.nextNoTrivia()
    addr = parseAddress(tokens)
    rbracket = tokens.nextNoTrivia()
    return MemoryNode(lbracket, addr, rbracket)

def parseBinary(tokens, left, currentPrecedence):
    """ Parses the right-hand side of a binary expression.

        mov  ax, [bx+si*2]
                     ^~~~
    """
    peek = tokens.peekNoTrivia().type
    while peek in precedence:
        
        tokPrec = precedence[peek]
    
        # If this is a binary operation that binds at least as tightly as the current operation,
        # consume it, otherwise we are done.
        if tokPrec > currentPrecedence:
            return left
    
        op = tokens.nextNoTrivia()
    
        # Parse the primary expression after the binary operator.
        right = parsePrimary(tokens)
    
        # If this binary operation binds less tightly with the rhs than the operator after the rhs, let
        # the pending operator take rhs as its lhs.
        nextPrec = precedence.get(tokens.peekNoTrivia().type, 10000)
        if tokPrec >= nextPrec:
            right = parseBinary(tokens, right, tokPrec)
    
        # Merge lhs/rhs.
        left = BinaryNode(left, op, right);
        peek = tokens.peekNoTrivia().type

    return left

def parseAddress(tokens):
    """ Parse an address inside a memory location:

        mov  ax, [bx+si]
                  ^~~~~
    """
    return parseArgument(tokens)

def parseLiteral(tokens):
    """ Parse a literal value in an instruction:

        mov  ax, 123
             ^~  ^~~
    """
    token = tokens.nextNoTrivia()
    if token.type == "integer":
        return IntegerNode(token)
    else:
        return IdentifierNode(token)

def parseParentheses(tokens):
    """ Parses a parenthesized expression.
    
        (1 + 3)
        ^~~~~~~
    """
    lparen = tokens.nextNoTrivia()
    expr = parseArgument(tokens)
    rparen = tokens.nextNoTrivia()
    return ParenthesesNode(lparen, expr, rparen)

def parsePrimary(tokens):
    """ Parse a primary expression:

        mov  ax, (1 + 3) << 2
             ^~  ^~~~~~~    ^
    """
    if tokens.peekNoTrivia().type == "lparen":
        return parseParentheses(tokens)
    else:
        return parseLiteral(tokens)

def parseInstruction(tokens):
    """ Parse a label or an instruction.
    
        example:
        ^~~~~~~~
            mov eax, ebx
            ^~~~~~~~~~~~
    """

    first = tokens.nextNoTrivia()

    # If a colon follows the first token, this is a label.
    if not tokens.isTrivia() and tokens.peekNoTrivia().type == "colon":
        label = LabelNode(first, tokens.nextNoTrivia())
        return label

    # Otherwise it's just an instruction.
    argList = parseArgumentList(tokens)
    return InstructionNode(first, argList)