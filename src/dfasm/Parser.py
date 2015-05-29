import Instructions
import Assembler
import Lexer
import Symbols
import math
import libdiagnostics
from Encoding import *
from libdiagnostics import DiagnosticsException

precedence = {
    "asterisk" : 0,
    "slash"    : 0,
    "percent"  : 0,
    "plus"     : 1,
    "minus"    : 1,
    "lshift"   : 2,
    "rshift"   : 2,
    "ampersand": 3,
    "bar"      : 4,
}

operations = {
    "plus"     : lambda a, b: a + b,
    "minus"    : lambda a, b: a - b,
    "asterisk" : lambda a, b: a * b,
    "slash"    : lambda a, b: a / b,
    "percent"  : lambda a, b: a % b,
    "ampersand": lambda a, b: a & b,
    "bar"      : lambda a, b: a | b,
    "lshift"   : lambda a, b: a << b,
    "rshift"   : lambda a, b: a >> b,
}

class TokenStream(object):
    """ Defines a token stream. Internally, this is a list of tokens, together
    with an index to scroll through it, and some document/log objects that are
    used to give useful diagnostics back to the user on parse failure. """

    def __init__(self, tokens, doc, log):
        self.tokens = tokens
        self.index = 0
        self.doc = doc
        self.log = log

    def endOfStream(self):
        """ Return a token representing the end of the current stream -- this
        is an instance method, since the location in the source code differs
        across token streams. """
        location = libdiagnostics.SourceLocation.End(self.doc)
        return Lexer.Token("", "end-of-stream", location)

    def remainingTokens(self):
        """ Return the list of remaining tokens in the stream. """
        return self.tokens[self.index:]

    def peek(self):
        """ Peeks a token from the token stream. """
        if self.index >= len(self.tokens):
            return self.endOfStream()
        return self.tokens[self.index]

    def peekNoTrivia(self):
        """ Peeks a non-trivia token from the token stream. """
        for token in self.remainingTokens():
            if not token.isTrivia():
                return token
        return self.endOfStream()

    def isEmpty(self):
        """ Finds out if the token stream is empty. """
        return self.index >= len(self.tokens)

    def isTrivia(self):
        """ Finds out if all future tokens in the token stream are trivia. """
        return all(item.isTrivia() for item in self.remainingTokens())

    def nextToken(self):
        """ Reads the next token from the token stream. """
        token = self.peek()
        self.index += 1
        return token

    def skipTrivia(self):
        """ Skips trivia tokens. """
        while self.peek().isTrivia():
            self.nextToken()

    def nextNoTrivia(self, tokenType = None):
        """ Reads the next non-trivia token. """
        self.skipTrivia()
        result = self.nextToken()
        if tokenType is not None and result.type != tokenType:
            errorMsg = "Expected token of type '%s', got token of " \
                       "type '%s' instead." % (tokenType, result.type)
            self.log.LogError("Unexpected token", errorMsg, result.location)
        return result
            

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
        if name in Instructions.registers:  # Maybe we'll get lucky and encounter a register.
            return Instructions.RegisterOperand(Instructions.registers[name])
        else:
            return Instructions.LabelOperand(name, size32)

    def __repr__(self):
        return "IdentifierNode(%r)" % self.token

class BinaryNode(object):
    """ Defines a syntax node that captures a binary expression. """
    def __init__(self, left, op, right):
        """ `left` and `right` are two child nodes representing the operands;
        `op` is a single token representing the operator. """
        self.left = left
        self.op = op
        self.right = right

    def toOperand(self, asm):
        """ Converts the binary node to an operand, trying to constant-fold in
        the process. """
        lhs = self.left.toOperand(asm)
        rhs = self.right.toOperand(asm)
        isImmediate = lambda x: isinstance(x, Instructions.ImmediateOperand)
        if isImmediate(lhs) and isImmediate(rhs):
            # Simplify the expression by evaluating it.
            result = operations[self.op.type](lhs.value, rhs.value)
            return Instructions.ImmediateOperand.createSigned(result)
        else:
            # Create a binary pseudo-operand (which MemoryNode can then examine).
            return Instructions.BinaryOperand(lhs, self.op.type, rhs)

    def __str__(self):
        return "%s %s %s" % (self.left, self.op, self.right)

    def __repr__(self):
        return "BinaryNode(%r, %r, %r)" % (self.left, self.op, self.right)

class MemoryNode(object):
    """ Defines a syntax node that refers to a memory location. """
    def __init__(self, lbracket, address, rbracket):
        """ `lbracket` and `rbracket` are tokens of the respective type;
        `address` is the syntax node representing a location in memory."""
        self.lbracket = lbracket
        self.address = address
        self.rbracket = rbracket

    @property
    def location(self):
        """ Gets this memory node's source location. """
        return self.lbracket.location.Between(self.rbracket.location)

    def getDisplacement(self, operand):
        """ Find the total displacement  of non-index operands represented
        by this node's address. """
        if isinstance(operand, Instructions.ImmediateOperand):
            return operand.value
        elif isinstance(operand, Instructions.BinaryOperand) and operand.op == "plus":
            return self.getDisplacement(operand.left) + self.getDisplacement(operand.right)
        elif isinstance(operand, Instructions.BinaryOperand) and operand.op == "minus":
            return self.getDisplacement(operand.left) - self.getDisplacement(operand.right)
        elif isinstance(operand, Instructions.RegisterOperand):
            return 0
        else:
            raise DiagnosticsException("Invalid memory operand", "Non-immediate SIB displacements are not supported.", self.location)

    def getIndexOperands(self, operand):
        """ Return a list of tuples (r, s), where r is a register and s is the
        left-shift amount (0, 1, 2, or 3). """
        
        if isinstance(operand, Instructions.RegisterOperand):
            return [(operand.register, 0)]
        elif isinstance(operand, Instructions.BinaryOperand):
            if operand.op in ("asterisk", "lshift"):
                left, right = operand.left, operand.right
                if operand.op == "asterisk" and isinstance(right, Instructions.RegisterOperand):
                    # Transform "4 * eax" into "eax * 4", first.
                    left, right = right, left

                # Disallow cases like "eax * ebx" and "2 << ebx".
                if not isinstance(right, Instructions.ImmediateOperand):
                    raise DiagnosticsException("Invalid memory operand", "'%s' is not allowed in a memory operand." % operand, self.location)
                
                # Then, calculate the shift amount for (eax << k) or (eax * k).
                shift = right.value
                if operand.op == "asterisk":
                    try:
                        factorToShift = {1: 0, 2: 1, 4: 2, 8: 3}
                        shift = factorToShift[shift]
                    except IndexError:
                        raise DiagnosticsException("Invalid memory operand", "Valid multiplicands for memory operands are 1, 2, 4 and 8; got %d." % shift, self.location)
                
                if not 0 <= shift <= 3:
                    raise DiagnosticsException("Invalid memory operand", "Valid shift amounts for memory operands are 0 through 3; got %d." % shift, self.location)
                return [(left.register, shift)]
                    
            elif operand.op == "plus":
                return self.getIndexOperands(operand.left) + self.getIndexOperands(operand.right)
            elif operand.op == "minus":
                if self.getIndexOperands(operand.right):
                    raise DiagnosticsException("Invalid memory operand", "Subtraction of memory index operands is not allowed.", self.location)
                else:
                    return self.getIndexOperands(operand.left)
            else:
                raise DiagnosticsException("Invalid memory operand", "'%s' is not allowed in a memory operand." % operand, self.location)
        return []

    def toOperand(self, asm):
        operand = self.address.toOperand(asm)
        disp = Instructions.ImmediateOperand.createSigned(self.getDisplacement(operand))
        indices = self.getIndexOperands(operand)
        baseRegisters  = [r      for (r, s) in indices if s == 0]
        indexRegisters = [(r, s) for (r, s) in indices if s != 0]

        if not indexRegisters and len(baseRegisters) == 1: # Simple
            [r] = baseRegisters
            return Instructions.MemoryOperand(r, disp, size8)
        elif len(baseRegisters) == 2: # Simple SIB
            [rB, rI] = baseRegisters
            return Instructions.SIBMemoryOperand(rB, rI, 0, disp, size8)
        elif len(baseRegisters) == 1 and len(indexRegisters) == 1: # Typical SIB
            [rB] = baseRegisters
            [(rI, sI)] = indexRegisters
            return Instructions.SIBMemoryOperand(rB, rI, sI, disp, size8)
        elif len(indices) > 2:
            raise DiagnosticsException("Invalid memory operand", "A memory operand contains at most two registers.", self.location)
        else:
<<<<<<< HEAD
            raise ValueError("Bad memory operand.")
=======
            # XXX: is mov eax, [ebx * 4] (i.e. only an index register, no base) valid?
            raise DiagnosticsException("Invalid memory operand", "Bad memory operand.", self.location)
>>>>>>> origin/master

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
            return "%s %s" % (self.separator, self.node)
        else:
            return str(self.node)

    def __repr__(self):
        return "SeparatedNode(%r, %r)" % (self.separator, self.node)

class SeparatedList(object):
    """ Defines a list of separated syntax nodes. """
    def __init__(self, nodes):
        self.nodes = nodes

    def __iter__(self):
        return iter(n.node for n in self.nodes)

    def toOperands(self, asm):
        return [n.toOperand(asm) for n in self.nodes]

    def __str__(self):
        return "".join(str(n) for n in self.nodes)

    def __repr__(self):
        return "SeparatedList(%r)" % self.nodes

class InstructionNode(object):
    """ Describes an instruction syntax node. """
    def __init__(self, mnemonic, argumentList):
        self.mnemonic = mnemonic
        self.argumentList = argumentList

    def __str__(self):
        return "%s %s" % (self.mnemonic, self.argumentList)

    def __repr__(self):
        return "InstructionNode(%r, %r)" % (self.mnemonic, self.argumentList)

class CastNode(object):
    """ Describes an explicit cast syntax node. """
    def __init__(self, type, ptr, expr):
        """ `type` is the type being cast to. `ptr` is a token containing the
        literal word "ptr". `expr` is the expression being cast. """
        self.type = type
        self.ptr = ptr
        self.expr = expr

    @property
    def size(self):
        try:
            return parseSize(self.type.contents)
        except IndexError:
            raise ValueError("Invalid data type '%s %s' in cast expression '%s'" %
                             (self.type, self.ptr, self))

    def toOperand(self, asm):
        """ Converts the cast node to an operand. """
        return self.expr.toOperand(asm).cast(self.size)

    def __str__(self):
        return "%s %s %s" % (self.type, self.ptr, self.expr)

    def __repr__(self):
        return "CastNode(%r, %r, %r)" % (self.type, self.ptr, self.expr)

class ParenthesesNode(object):
    """ Represents a parenthesized syntax node. """
    def __init__(self, lparen, expr, rparen):
        """ `expr` is the expression parenthesized, and `lparen` and `rparen`
        are its surrounding parenthesis tokens. """
        self.lparen = lparen
        self.expr = expr
        self.rparen = rparen

    def toOperand(self, asm):
        """ Converts the parenthesized node to an operand. """
        return self.expr.toOperand(asm)

    def __str__(self):
        return "%s%s%s" % (self.lparen, self.expr, self.rparen)

    def __repr__(self):
        return "ParenthesesNode(%r, %r, %r)" % (self.lparen, self.expr, self.rparen)

class LabelNode(object):
    """ Describes a label syntax node. """
    def __init__(self, name, colon):
        """ `name` is a token containing the label name, and `colon` is the
        colon token that follows it. """
        self.name = name
        self.colon = colon

    def __str__(self):
        return "%s%s" % (self.name, self.colon)

    def __repr__(self):
        return "LabelNode(%r, %r)" % (self.name, self.colon)

class DirectiveNodeBase(object):
    """ A base class for assembler directives. """
    pass

class GlobalDirective(DirectiveNodeBase):
    """ A global assembler directive, declaring an external symbol, such as
    ".globl main". """
    def __init__(self, dot, globl, name):
        """ `dot` and `globl` are tokens containing the directive; `name` is
        a token containing its argument. """
        self.dot = dot
        self.globl = globl
        self.name = name

    def __str__(self):
        return "%s%s %s" % (self.dot, self.globl, self.name)

    def __repr__(self):
        return "GlobalDirective(%r, %r, %r)" % (self.dot, self.globl, self.name)

    def apply(self, asm):
        """ Make the specified symbol public. """
        asm.getSymbol(self.name.contents).makePublic()

class ExternDirective(DirectiveNodeBase):
    def __init__(self, dot, extern, name):
        """ `dot` and `extern` are tokens containing the directive; `name` is
        a token containing its argument. """
        self.dot = dot
        self.extern = extern
        self.name = name

    def __str__(self):
        return "%s%s %s" % (self.dot, self.extern, self.name)

    def __repr__(self):
        return "ExternDirective(%r, %r, %r)" % (self.dot, self.extern, self.name)

    def apply(self, asm):
        """ Define the given symbol as an external one. """
        asm.defineSymbol(Symbols.ExternalSymbol(self.name.contents))

class IntegerDataDirective(DirectiveNodeBase):
    def __init__(self, dot, typeToken, size, dataList):
        """ `dot` and `typeToken` are tokens containing the directive; `size`
        is the size of each argument (an OperandSize instance), and `dataList`
        is a SeparatedList containing the arguments as syntax nodes. """
        self.dot = dot
        self.typeToken = typeToken
        self.size = size
        self.dataList = dataList

    def __str__(self):
        return "%s%s %s" % (self.dot, self.typeToken, self.dataList)

    def __repr__(self):
        return "IntegerDataDirective(%r, %r, %r, %r)" % (self.dot, self.typeToken, self.size, self.dataList)

    def apply(self, asm):
        for operand in self.dataList.toOperands(asm):
            if not isinstance(operand, Instructions.ImmediateOperandBase):
                raise ValueError("'.%s' directive arguments must be immediate operands."
                                 % self.typeToken)
            val = operand.toUnsigned()
            maxSize = 2 ** (self.size.size * 8) - 1
            if not 0 <= operand.value <= maxSize:
                raise ValueError("'.%s' directive arguments must be in the 0-%d range."
                                 % (self.typeToken, maxSize))
            asm.writeArgument(operand.cast(self.size))

class DataArrayDirective(DirectiveNodeBase):
    def __init__(self, dot, typeToken, arrayToken, size, length, element):
        """ `dot`, `typeToken` and `arrayToken` contain the header, of the form
        
            .<type> array

        `size` is the size of each element (an OperandSize instance), `length`
        is the number of times to repeat the value argument (as a syntax node
        implementing `toOperand()`) and `element` is the repeated value (idem).
        """
        self.dot = dot        
        self.typeToken = typeToken
        self.arrayToken = arrayToken
        self.size = size
        self.length = length
        self.element = element

    def headerStr(self):
        return "%s%s %s" % (self.dot, self.typeToken, self.arrayToken)

    def __str__(self):
        return "%s %s %s" % (self.headerStr(), self.length, self.element)

    def __repr__(self):
        return "DataArrayDirective(%r, %r, %r, %r, %r, %r)" \
            % (self.dot, self.typeToken, self.arrayToken, self.size, self.length, self.element)

    def apply(self, asm):
        elem = self.element.toOperand(asm)
        arrLengthOp = self.length.toOperand(asm)
        if not isinstance(elem, Instructions.ImmediateOperandBase):
            raise ValueError("'%s' directive element must be an immediate operand." % self.headerStr())
        if not isinstance(arrLengthOp, Instructions.ImmediateOperandBase):
            raise ValueError("'%s' directive array size must be an immediate operand." % self.headerStr())
        
        arrLength = arrLengthOp.value
        if arrLength < 0:
            raise ValueError("'%s' directive array size may not be negative." % self.headerStr())

        maxSize = 2 ** (self.size.size * 8) - 1
        if not 0 <= elem.value <= maxSize:
            raise ValueError("'%s' directive element must be in the 0-%d range."
                             % (self.headerStr(), maxSize))

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
    if tokens.peekNoTrivia().type == "integer":
        return IntegerNode(tokens.nextNoTrivia())
    else:
        return IdentifierNode(tokens.nextNoTrivia("identifier"))

def parseParentheses(tokens):
    """ Parses a parenthesized expression.
    
        (1 + 3)
        ^~~~~~~
    """
    lparen = tokens.nextNoTrivia("lparen")
    expr = parseArgument(tokens)
    rparen = tokens.nextNoTrivia("rparen")
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

    dirName = tokens.nextNoTrivia("identifier")
    if dirName.contents == "globl" or dirName.contents == "global":
        symName = tokens.nextNoTrivia("identifier")
        return GlobalDirective(dot, dirName, symName)
    elif dirName.contents == "extrn" or dirName.contents == "extern":
        symName = tokens.nextNoTrivia("identifier")
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
        raise ValueError("Unrecognized assembler directive '" + str(dot) + str(dirName) + "'")
    

def parseInstruction(tokens):
    """ Parse a label, directive or instruction.
        
        .globl example
        ^~~~~~~~~~~~~~
        example:
        ^~~~~~~~
            mov eax, ebx
            ^~~~~~~~~~~~
    """

    if tokens.peekNoTrivia().type == "dot":
        return parseDirective(tokens, tokens.nextNoTrivia())

    first = tokens.nextNoTrivia("identifier")        

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