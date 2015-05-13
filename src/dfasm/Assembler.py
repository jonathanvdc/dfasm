from Parser import *
from Encoding import *

def writeSimpleInstruction(name, opCode, asm, args):
    if len(args) > 0:
        raise SyntaxError("'" + name + "' does not take any arguments.")
    asm.write(opCode)

def writeBinaryInstruction(name, opCode, asm, args):
    if len(args) != 2:
        raise SyntaxError("'" + name + "' takes precisely two arguments.")
    reverseArgs = args[1].addressingMode != "register"
    regArg, memArg = (args[0], args[1]) if reverseArgs else (args[1], args[0])

    if regArg.addressingMode != "register":
        raise Exception("'" + name + "' must take at least one register operand.")

    if memArg.operandSize != regArg.operandSize:
        memArg = memArg.cast(regArg.operandSize) # Cast if necessary

    isWord = regArg.operandSize > size8

    mode = encodeAddressingMode(memArg.addressingMode)
    regIndex = regArg.operandIndex
    memIndex = memArg.operandIndex

    opcodeByte = opCode << 2 | (int(reverseArgs) & 0x01) << 1 | int(isWord) & 0x01
    operandsByte = mode << 6 | regIndex << 3 | memIndex

    asm.write([opcodeByte, operandsByte])
    memArg.writeDataTo(asm)

def writeBinaryImmediateInstruction(name, opCode, asm, args):
    if len(args) != 2:
        raise SyntaxError("'" + name + "' takes precisely two arguments.")

    memArg, immArg = args[0], args[1]

    wordReg = memArg.operandSize > size8

    if immArg.operandSize == size0:
        immArg = immArg.cast(size8)
    elif immArg.operandSize != size8:
        if not wordReg:
            raise Exception("Cannot use an immediate larger than 8 bits ('" + str(immArg) + "') with 8-bit register '" + str(memArg) + "'")
        immArg = immArg.cast(memArg.operandSize)
        
    shortImm = immArg.operandSize != memArg.operandSize

    mode = encodeAddressingMode(memArg.addressingMode)
    memIndex = memArg.operandIndex

    opcodeByte = 0x80 | (int(shortImm) & 0x01) << 1 | int(wordReg) & 0x01
    operandsByte = mode << 6 | opCode << 3 | memIndex
    asm.write([opcodeByte, operandsByte])
    memArg.writeDataTo(asm)
    immArg.writeDataTo(asm)

def writePrefixedInstruction(prefix, instructionBuilder, asm, args):
    asm.write([prefix])
    instructionBuilder(asm, args)

def writeAmbiguousBinaryInstruction(registerInstructionBuilder, immediateInstructionBuilder, asm, args):
    if len(args) > 1 and isinstance(args[1], Instructions.ImmediateOperand):
        immediateInstructionBuilder(asm, args)
    else:
        registerInstructionBuilder(asm, args)

def definePrefixedInstruction(prefix, instructionBuilder):
    return lambda asm, args: writePrefixedInstruction(prefix, instructionBuilder, asm, args)

def defineSimpleInstruction(name, opCode):
    return lambda asm, args: writeSimpleInstruction(name, opCode, asm, args)

def defineBinaryInstruction(name, opCode):
    return lambda asm, args: writeBinaryInstruction(name, opCode, asm, args)

def defineBinaryImmediateInstruction(name, opCode):
    return lambda asm, args: writeBinaryImmediateInstruction(name, opCode, asm, args)

def defineAmbiguousBinaryInstruction(name, immOpCode, opCode = None):
    if opCode is None:
        opCode = immOpCode << 1
    binDef = defineBinaryInstruction(name, opCode)
    immDef = defineBinaryImmediateInstruction(name, immOpCode)
    return lambda asm, args: writeAmbiguousBinaryInstruction(binDef, immDef, asm, args)

def defineExtendedBinaryInstruction(name, prefix, opCode):
    return definePrefixedInstruction(prefix, defineBinaryInstruction(name, opCode))

addressingModeEncodings = {
    "register" : 3,
    "memory" : 0,
    "memoryByteOffset" : 1,
    "memoryWordOffset" : 2
}

def encodeAddressingMode(mode):
    return addressingModeEncodings[mode]

instructionBuilders = {
    "pause" : defineSimpleInstruction("pause", 0x90),
    "clc"   : defineSimpleInstruction("clc", 0xf8),
    "stc"   : defineSimpleInstruction("stc", 0xf9),
    "mov"   : defineBinaryInstruction("mov", 0x22),
    "add"   : defineAmbiguousBinaryInstruction("add", 0x00),
    "sub"   : defineAmbiguousBinaryInstruction("sub", 0x05),
    "and"   : defineAmbiguousBinaryInstruction("and", 0x04),
    "or"    : defineAmbiguousBinaryInstruction("or", 0x01),
    "xor"   : defineAmbiguousBinaryInstruction("xor", 0x06),
    "imul"  : defineExtendedBinaryInstruction("imul", 0x0f, 0x2b), # imul and idiv are *not* working properly!
    "idiv"  : defineBinaryInstruction("idiv", 0x3d)
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

    def write(self, bytes):
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