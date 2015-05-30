from Parser import *
from Encoding import *
import Symbols

from Builders import builders

class Assembler(object):
    """ Converts a list of instructions and labels to bytecode. """

    def __init__(self, baseOffset = None, relocateAbsolutes = True):
        # A list of byte values representing the bytecode.
        self.code = []

        # The base offset is absolutely necessary for absolute things,
        # but we may choose to provide it later on.
        self.baseOffset = baseOffset

        # This boolean value tells symbol operands whether they should try
        # to fix up absolute offsets themselves, or report a pseudo-offset of 0,
        # making it the linker's problem.
        self.relocateAbsolutes = relocateAbsolutes

        # A dictionary of symbols (these include labels).
        self.symbols = {}

        # A list of relocation records, which are SymbolOperand objects.
        self.relocations = []

        self.index = 0

    def getSymbol(self, name):
        """ Gets the symbol with the given name. 
            If no such symbol exists, one will be appointed to you.  """
        if not self.hasSymbol(name):
            self.defineSymbol(Symbols.LocalSymbol(name))
        return self.symbols[name]

    def getSymbolAt(self, offset):
        """ Gets the symbol at the given offset. 
            If no such symbol exists, one will be appointed to you.  """
        for item in self.symbols:
            if item.offset == offset:
                return item
        return self.defineSymbol(Symbols.LocalSymbol("#" + hex(offset), offset))

    def hasSymbol(self, name):
        """ Finds out if there is a symbol with the given name. """
        return name in self.symbols

    def defineSymbol(self, symbol):
        """ Defines a symbol. """
        if self.hasSymbol(symbol.name):
            self.symbols[symbol.name].define(symbol)
        else:
            self.symbols[symbol.name] = symbol

        return self.getSymbol(symbol.name)

    def patchLabels(self):
        """ Patches all labels. """
        i = 0
        while i < len(self.code):
            if isinstance(self.code[i], Instructions.Operand) and self.code[i].canWrite(self):
                self.code[i:i+1] = self.code[i].getData(self)
            i += 1

    def assemble(self, nodes):
        """ Assemble the given list of instructions and labels into bytecode
        and return the resulting list of bytes. """

        for item in nodes:
            self.process(item)

        patchLabels()

        return self.code

    def process(self, node):
        if isinstance(node, LabelNode):
            self.defineSymbol(Symbols.LocalSymbol(node.name.contents, self.index, False))
        elif isinstance(node, InstructionNode):
            self.processInstruction(node)
        elif isinstance(node, DirectiveNodeBase):
            node.apply(self)
        else:
            raise ValueError('invalid assembly node')

    def writeArgument(self, arg):
        """ Writes an argument, possibly resolving it later on. """
        if arg.canWrite(self):
            arg.writeDataTo(self)
        else:
            self.code += [arg]
            self.index += arg.dataSize

    def write(self, bytes):
        """ Write several bytes to our bytecode list. """
        self.code += bytes
        self.index += len(bytes)

    def processInstruction(self, node):
        """ Process the given InstructionNode. """
        op = str(node.mnemonic)

        if op in builders:
            builders[op](self, node.argumentList.toOperands(self))
        else:
            raise ValueError('unknown opcode')