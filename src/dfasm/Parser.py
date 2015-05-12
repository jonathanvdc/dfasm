
class TokenStream(object):
    """ Defines a token stream. """ 
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        """ Peeks a token from the token stream. """
        return self.tokens[self.index]

    def peekNoTrivia(self):
        """ Peeks a non-trivia token from the token stream. """
        result = self.peek()
        i = 1
        while result.isTrivia():
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
            raise StopIteration
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

    def __repr__(self):
        return "IntegerNode(%r)" % self.token

class IdentifierNode(LiteralNode):
    """ Describes an identifier syntax node. """

    def __repr__(self):
        return "IdentifierNode(%r)" % self.token

class AddressNode(object):
    """ Defines a syntax node that captures an address expression. """
    def __init__(self, base, asterisk, factor, plus, offset):
        self.base = base
        self.asterisk = asterisk
        self.factor = factor
        self.plus = plus
        self.offset = offset

    def __str__(self):
        if self.asterisk is None and self.plus is None:
            return str(self.base)
        elif self.asterisk is None:
            return str(self.base) + " " + str(self.plus) + " " + str(self.offset)
        elif self.plus is None:
            return str(self.base) + " " + str(self.asterisk) + " " + str(self.factor)
        else:
            return str(self.base) + " " + str(self.asterisk) + " " + str(self.factor) + " " + str(self.plus) + " " + str(self.offset)

    def __repr__(self):
        return "BinaryNode(%r, %r, %r, %r, %r)" % (self.base, self.asterisk, self.factor, self.plus, self.offset)

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
        return parseLiteral(tokens)

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

def parseAddress(tokens):
    """ Parse an address inside a memory location:

        mov  ax, [bx+si]
                  ^~~~~
    """
    base = parseLiteral(tokens)
    op = tokens.peekNoTrivia()
    if op.type == "asterisk":
        asterisk = tokens.nextNoTrivia()
        factor = parseLiteral(tokens)
        if tokens.peekNoTrivia().type == "plus":
            plus = tokens.nextNoTrivia()
            offset = parseLiteral(tokens)
            return AddressNode(base, asterisk, factor, plus, offset)
        else:
            return AddressNode(base, asterisk, factor, None, None)
    elif op.type == "plus":
        plus = tokens.nextNoTrivia()
        offset = parseLiteral(tokens)
        return AddressNode(base, None, None, plus, offset)
    else:
        return AddressNode(base, None, None, None, None)

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