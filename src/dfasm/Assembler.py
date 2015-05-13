from Parser import *
from Encoding import *

def writeSimpleInstruction(name, opCode, asm, args):
    if len(args) > 0:
        raise SyntaxError("'" + name + "' does not take any arguments.")
    asm.write(opCode)

def writeBinaryInstruction(name, opCode, asm, args):
    if len(args) != 2:
        raise SyntaxError("'" + name + "' takes precisely two arguments.")
    reverseArgs = args[0].addressingMode != "register"
    regArg, memArg = (args[1], args[0]) if reverseArgs else (args[0], args[1])

    if memArg.operandSize != regArg.operandSize:
        memArg = memArg.cast(regArg.operandSize) # Cast if necessary

    isWord = regArg.operandSize > size8

    mode = encodeAddressingMode(memArg.addressingMode)
    regIndex = regArg.operandIndex
    memIndex = memArg.operandIndex

    opcodeByte = opCode << 2 | int(reverseArgs) & 0x01 << 1 | int(isWord) & 0x01
    operandsByte = mode << 6 | memIndex << 3 | regIndex

    asm.write(opcodeByte)
    asm.write(operandsByte)
    memArg.writeDataTo(asm)

def createSimpleInstructionBuilder(name, opCode):
    return lambda asm, args: writeSimpleInstruction(name, opCode, asm, args)

def createBinaryInstructionBuilder(name, opCode):
    return lambda asm, args: writeBinaryInstruction(name, opCode, asm, args)

addressingModeEncodings = {
    "register" : 3,
    "memory" : 0,
    "memoryByteOffset" : 1,
    "memoryWordOffset" : 2
}

def encodeAddressingMode(mode):
    return addressingModeEncodings[mode]

instructionBuilders = {
    "pause" : createSimpleInstructionBuilder("pause", 0x90),
    "clc"   : createSimpleInstructionBuilder("clc", 0xf8),
    "stc"   : createSimpleInstructionBuilder("stc", 0xf9),
    "mov"   : createBinaryInstructionBuilder("mov", 0x22)
    # TODO: the literal entirety of x86.
}

class Assembler(object):
    """ Converts a list of instructions and labels to bytecode. """

    def __init__(self):
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

    def patchLabels(self):
        """ Patches all labels. """
        for addr, label, func in replacements:
            new = func(labels[label])
            self.code[addr:addr + len(new)] = new

    def assemble(self, nodes):
        """ Assemble the given list of instructions and labels into bytecode
        and return the resulting list of bytes. """

        for item in nodes:
            self.process(item)

        patchLabels()

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

        if op in instructionBuilders:
            instructionBuilders[op](self, node.argumentList.toOperands(self))
        else:
            raise ValueError('unknown opcode')