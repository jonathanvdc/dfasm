import Instructions
import Assembler
import Lexer
import Symbols
import math
import libdiagnostics
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
    def __init__(self, tokens, doc):
        self.tokens = tokens
        self.doc = doc
        self.index = 0

    def peek(self):
        """ Peeks a token from the token stream. """
        if self.index >= len(self.tokens):
            return Lexer.Token("", "end-of-stream", libdiagnostics.SourceLocation(self.doc, self.doc.Source.Length - 1, 1))
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
            return Lexer.Token("", "end-of-stream", libdiagnostics.SourceLocation(self.doc, self.doc.Source.Length - 1, 1))
        i = self.index
        self.index += 1
        return self.tokens[i]

    def skipTrivia(self):
        """ Skips trivia tokens. """
        while self.peek().isTrivia():
            self.nextToken()

    def nextNoTrivia(self, tokenType = None):
        """ Reads the next non-trivia token. """
        self.skipTrivia()
        out = self.nextToken()
        if not (tokenType == None) and out.type != tokenType:
            print("Error: Expected token of type " + tokenType + ", got token of type " + out.type + " instead.")
        return out
            

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
        return Instructions.ImmediateOperand.createSigned(val)

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
            return Instructions.LabelOperand(name, size32)


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
            return Instructions.ImmediateOperand.createSigned(operations[self.op.type](lhs.value, rhs.value))
        else:
            return Instructions.BinaryOperand(lhs, self.op.type, rhs) # Create a binary pseudo-operand (which MemoryNode can then examine)

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

    def getDisplacement(self, operand):
        if isinstance(operand, Instructions.ImmediateOperand):
            return operand.value
        elif isinstance(operand, Instructions.BinaryOperand) and operand.op == "plus":
            return self.getDisplacement(operand.left) + self.getDisplacement(operand.right)
        elif isinstance(operand, Instructions.BinaryOperand) and operand.op == "minus":
            return self.getDisplacement(operand.left) - self.getDisplacement(operand.right)
        else:
            return 0

    def getIndexOperands(self, operand):
        if isinstance(operand, Instructions.RegisterOperand):
            return [(operand.register, 0)]
        elif isinstance(operand, Instructions.BinaryOperand):
            if operand.op == "asterisk" or operand.op == "lessthanlessthan":
                if isinstance(operand.left, Instructions.RegisterOperand) and isinstance(operand.right, Instructions.ImmediateOperand):
                    return [(operand.left.register, operand.right.value if operand.op == "lessthanlessthan" else int(math.log(operand.right.value, 2)))]
                elif isinstance(operand.right, Instructions.RegisterOperand) and isinstance(operand.left, Instructions.ImmediateOperand):
                    return [(operand.right.register, operand.left.value if operand.op == "lessthanlessthan" else int(math.log(operand.left.value, 2)))]
                else:
                    raise Exception("Memory operands do not support complex operations on registers, such as '" + str(operand) + "'")
            elif operand.op == "plus":
                return self.getIndexOperands(operand.left) + self.getIndexOperands(operand.right)
            elif operand.op == "minus" and len(self.getIndexOperands(operand.right)) == 0:
                return self.getIndexOperands(operand.left)
            else:
                raise Exception("Memory operands do not support complex operations on registers, such as '" + str(operand) + "'")
        return []

    def toOperand(self, asm):
        addrOp = self.address.toOperand(asm)
        disp = Instructions.ImmediateOperand.createSigned(self.getDisplacement(addrOp))
        indices = self.getIndexOperands(addrOp)
        baseRegisters = map(lambda x: x[0], filter(lambda x: x[1] == 0, indices)) # Make index registers addressed as `eax * 1` or `ebx << 0` base registers.
        indices = filter(lambda x: x[1] != 0, indices)
        if len(indices) == 0 and len(baseRegisters) == 1: # Simple
            return Instructions.MemoryOperand(baseRegisters[0], disp, size8)
        elif len(baseRegisters) == 2: # Simple SIB
            return Instructions.SIBMemoryOperand(baseRegisters[0], baseRegisters[1], 0, disp, size8)
        elif len(baseRegisters) == 1 and len(indices) == 1: # Typical SIB
            return Instructions.SIBMemoryOperand(baseRegisters[0], indices[0][0], indices[0][1], disp, size8)
        elif len(baseRegisters) > 2: # Whaaaat?
            raise Exception("More than two base registers are not supported. ('" + str(self) + "')") 
        elif len(indices) > 2:
            raise Exception("More than two index registers are not supported. ('" + str(self) + "')") 
        else:
            raise Exception("Bad memory operand ('" + str(self) + "')")

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

class CastNode(object):
    """ Describes an explicit cast syntax node. """
    def __init__(self, type, ptr, expr):
        self.type = type
        self.ptr = ptr
        self.expr = expr

    @property
    def size(self):
        try:
            return parseSize(self.type.contents)
        except:
            raise Exception("Invalid data type '" + str(self.type) + " " + str(self.ptr) + "' in cast expression '" + str(self) + "'")
            
    def toOperand(self, asm):
        """ Converts the cast node to an operand. """
        return self.expr.toOperand(asm).cast(self.size)

    def __str__(self):
        return str(self.type) + " " + str(self.ptr) + " " + str(self.expr)

    def __repr__(self):
        return "CastNode(%r, %r, %r)" % (self.type, self.ptr, self.expr)

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

class DirectiveNodeBase(object):
    """ A base class for assembler directives. """
    pass

class GlobalDirective(DirectiveNodeBase):
    def __init__(self, dot, globl, name):
        self.dot = dot
        self.globl = globl
        self.name = name

    def __str__(self):
        return str(self.dot) + str(self.globl) + " " + str(self.name)

    def __repr__(self):
        return "GlobalDirective(%r, %r, %r)" % (self.dot, self.globl, self.name)

    def apply(self, asm):
        asm.getSymbol(self.name.contents).makePublic()

class ExternDirective(DirectiveNodeBase):
    def __init__(self, dot, extern, name):
        self.dot = dot
        self.extern = extern
        self.name = name

    def __str__(self):
        return str(self.dot) + str(self.extern) + " " + str(self.name)

    def __repr__(self):
        return "ExternDirective(%r, %r, %r)" % (self.dot, self.extern, self.name)

    def apply(self, asm):
        asm.defineSymbol(Symbols.ExternalSymbol(self.name.contents))

class IntegerDataDirective(DirectiveNodeBase):
    def __init__(self, dotToken, typeToken, size, dataList):
        self.dotToken = dotToken
        self.typeToken = typeToken
        self.size = size
        self.dataList = dataList

    def __str__(self):
        return str(self.dotToken) + str(self.typeToken) + " " + str(self.dataList)

    def __repr__(self):
        return "IntegerDataDirective(%r, %r, %r, %r)" % (self.dotToken, self.typeToken, self.size, self.dataList)

    def apply(self, asm):
        for item in self.dataList.toOperands(asm):
            if not isinstance(item, Instructions.ImmediateOperandBase):
                raise Exception("'." + str(self.typeToken) + "' directive arguments must be immediate operands.")
            val = item.toUnsigned()
            maxSize = 2 ** (self.size.size * 8) - 1
            if item.value < 0 or item.value > maxSize:
                raise Exception("'." + str(self.typeToken) + "' directive arguments must be in the 0-" + str(maxSize) + " range.")
            asm.writeArgument(item.cast(self.size))

class DataArrayDirective(DirectiveNodeBase):
    def __init__(self, dotToken, typeToken, arrayToken, size, length, element):
        self.dotToken = dotToken        
        self.typeToken = typeToken
        self.arrayToken = arrayToken
        self.size = size
        self.length = length
        self.element = element

    def headerStr(self):
        return str(self.dotToken) + str(self.typeToken) + " " + str(self.arrayToken)

    def __str__(self):
        return self.headerStr() + " " + str(self.length) + " " + str(self.element)

    def __repr__(self):
        return "DataArrayDirective(%r, %r, %r, %r, %r, %r)" % (self.dotToken, self.typeToken, self.arrayToken, self.size, self.length, self.element)

    def apply(self, asm):
        elem = self.element.toOperand(asm)
        arrLengthOp = self.length.toOperand(asm)
        if not isinstance(elem, Instructions.ImmediateOperandBase):
            raise Exception("'" + self.headerStr() + "' directive element must be an immediate operand.")
        if not isinstance(arrLengthOp, Instructions.ImmediateOperandBase):
            raise Exception("'" + self.headerStr() + "' directive array size must be immediate operands.")
        arrLength = arrLengthOp.value
        if arrLength < 0:
            raise Exception("'" + self.headerStr() + "' directive array size must be greater than or equal to zero.")

        maxSize = 2 ** (self.size.size * 8) - 1
        if elem.value < 0 or elem.value > maxSize:
            raise Exception("'" + self.headerStr() + "' directive element must be in the 0-" + str(maxSize) + " range.")

        arrElem = elem.toUnsigned().cast(self.size)

        for i in range(arrLength):
            asm.writeArgument(arrElem)

def parseArgument(tokens):
    """ Parse an argument to an instruction:

        mov  ax, [bx+si]
             ^~  ^~~~~~~
    """
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
    lbracket = tokens.nextNoTrivia("lbracket")
    addr = parseAddress(tokens)
    rbracket = tokens.nextNoTrivia("rbracket")
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

def parseCast(tokens):
    """ Parses an explicit cast syntax node.
   
        inc dword ptr [eax]
            ^~~~~~~~~~~~~~~
    """
    typeToken = tokens.nextNoTrivia()
    if tokens.peekNoTrivia().contents == "ptr":
        ptrToken = tokens.nextNoTrivia()
    else:
        ptrToken = Lexer.Token("ptr", "identifier")
    return CastNode(typeToken, ptrToken, parsePrimary(tokens))

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
    peek = tokens.peekNoTrivia()
    if peek.type == "lparen":
        return parseParentheses(tokens)
    elif peek.type == "lbracket":
        return parseMemory(tokens)
    elif peek.type == "identifier" and isSize(peek.contents):
        return parseCast(tokens)
    else:
        return parseLiteral(tokens)

def parseDirective(tokens, dot):
    """ Parses an assembler directive.

        .globl example
        ^~~~~~~~~~~~~~
    """

    dirName = tokens.nextNoTrivia()
    if dirName.contents == "globl" or dirName.contents == "global":
        symName = tokens.nextNoTrivia()
        return GlobalDirective(dot, dirName, symName)
    elif dirName.contents == "extrn" or dirName.contents == "extern":
        symName = tokens.nextNoTrivia()
        return ExternDirective(dot, dirName, symName)
    elif isSize(dirName.contents):
        if tokens.peekNoTrivia().contents == "array":
            arrTok = tokens.nextNoTrivia()
            length = parseArgument(tokens)
            elem = parseArgument(tokens)
            return DataArrayDirective(dot, dirName, arrTok, parseSize(dirName.contents), length, elem)
        else:
            args = parseArgumentList(tokens)
            return IntegerDataDirective(dot, dirName, parseSize(dirName.contents), args)
    else:
        raise Exception("Unrecognized assembler directive '" + str(dot) + str(dirName) + "'")
    

def parseInstruction(tokens):
    """ Parse a label, directive or instruction.
        
        .globl example
        ^~~~~~~~~~~~~~
        example:
        ^~~~~~~~
            mov eax, ebx
            ^~~~~~~~~~~~
    """

    first = tokens.nextNoTrivia()

    if first.type == "dot":
        return parseDirective(tokens, first)

    # If a colon follows the first token, this is a label.
    if not tokens.isTrivia() and tokens.peekNoTrivia().type == "colon":
        label = LabelNode(first, tokens.nextNoTrivia())
        return label

    # Otherwise it's just an instruction.
    argList = parseArgumentList(tokens)
    return InstructionNode(first, argList)

def parseAllInstructions(tokens):
    """ Parses all instructions in the token stream. """
    results = []
    while not tokens.isTrivia():
        results.append(parseInstruction(tokens))
    return results