from Parser import *

def to8(x):
    """ Convert a given integer to a single-byte list. """
    return [x & 0xFF]

def to16le(x):
    """ Convert a given integer to its 16-bit little endian representation as
    a list of two bytes. """
    return [(x >>  0) & 0xFF,
            (x >>  8) & 0xFF]

def to32le(x):
    """ Convert a given integer to its 32-bit little endian representation as
    a list of four bytes. """
    return [(x >>  0) & 0xFF,
            (x >>  8) & 0xFF,
            (x >> 16) & 0xFF,
            (x >> 24) & 0xFF]

def relative(enc, here):
    """ Given an address encoding function and an offset, return a new
    function that encodes addresses relative to the given offset."""
    return lambda x: enc(x - here)

class Assembler(object):
    """ Converts a list of instructions and labels to bytecode. """

    def __init__(self, nodes):
        self.nodes = nodes

    def assemble(self):
        """ Assemble the given list of instructions and labels into bytecode
        and return the resulting list of bytes. """

        # Maps label names to their addresses when they are encountered.
        self.labels = {}

        # A list of byte values representing the bytecode.
        self.code = []
        self.index = 0

        # A list [(address, 'label name', func)] of replacements to make at
        # the specified addresses: this is done after processing all nodes.
        # `func` is a function that takes the address of a label and returns
        # a list of bytes; for example, if we need an 8-bit relative jump we
        # might append `lambda lbl: to8(lbl - here)`.
        self.replacements = []

        for node in self.nodes:
            self.process(node)

        for addr, label, func in replacements:
            new = func(labels[label])
            self.code[addr:addr + len(new)] = new

        return self.code

    def process(self, node):
        if isinstance(node, LabelNode):
            self.labels[str(node.name)] = self.index
        elif isinstance(node, InstructionNode):
            self.processInstruction(node)
        else:
            raise ValueError('invalid assembly node')

    def write(self, *bytes):
        """ Write several bytes to our bytecode list. """
        self.code += bytes
        self.index += len(bytes)

    def processInstruction(self, node):
        """ Process the given InstructionNode. """
        op = str(node.mnemonic)
        if op == 'pause':
            self.write(0x90)
        elif op == 'clc':
            self.write(0xf8)
        elif op == 'stc':
            self.write(0xf9)
        # TODO: the literal entirety of x86.
        else:
            raise ValueError('unknown opcode')