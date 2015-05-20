from Parser import *
from Encoding import *

def writeSimpleInstruction(name, opCode, asm, args):
    if len(args) > 0:
        raise Exception("'" + name + "' does not take any arguments.")
    asm.write(opCode)

def createModRM(mode, regIndex, memIndex):
    """ Created a MOD R/M byte. """
    return encodeAddressingMode(mode) << 6 | regIndex << 3 | memIndex

def writeBinaryInstruction(name, opCode, asm, args, needCast):
    if len(args) != 2:
        raise Exception("'" + name + "' takes precisely two arguments.")
    reverseArgs = args[0].addressingMode != "register"
    regArg, memArg = (args[1], args[0]) if reverseArgs else (args[0], args[1])

    if regArg.addressingMode != "register":
        raise Exception("'" + name + "' must take at least one register operand.")

    if needCast and memArg.operandSize != regArg.operandSize:
        memArg = memArg.cast(regArg.operandSize) # Cast if necessary

    isWord = memArg.operandSize > size8
    regIndex = regArg.operandIndex
    memIndex = memArg.operandIndex

    opcodeByte = opCode << 2 | (int(not reverseArgs) & 0x01) << 1 | int(isWord) & 0x01
    operandsByte = createModRM(memArg.addressingMode, regIndex, memIndex)

    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(memArg)

def writeBinaryImmediateInstruction(name, opCode, asm, args):
    if len(args) != 2:
        raise Exception("'" + name + "' takes precisely two arguments.")

    memArg, immArg = args[0], args[1]

    wordReg = memArg.operandSize > size8

    if immArg.operandSize == size0:
        immArg = immArg.cast(size8)
    elif immArg.operandSize != size8:
        if not wordReg:
            raise Exception("Cannot use an immediate larger than 8 bits ('" + str(immArg) + "') with 8-bit register '" + str(memArg) + "'")
        immArg = immArg.cast(memArg.operandSize)
        
    shortImm = immArg.operandSize != memArg.operandSize

    opcodeByte = 0x80 | (int(shortImm) & 0x01) << 1 | int(wordReg) & 0x01
    operandsByte = createModRM(memArg.addressingMode, opCode, memArg.operandIndex)
    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(memArg)
    asm.writeArgument(immArg)

def writeMovImmediateInstruction(asm, args):
    if len(args) != 2:
        raise Exception("'mov' takes precisely two arguments.")

    memArg, immArg = args[0], args[1]

    if memArg.addressingMode == "register":
        asm.write([0xb << 4 | (int(memArg.operandSize != size8) & 0x01) << 3 | memArg.operandIndex])
    else:
        asm.write([0xc6 | (int(memArg.operandSize != size8) & 0x01)])
        asm.write([createModRM(memArg.addressingMode, 0x00, memArg.operandIndex)])
        asm.writeArgument(memArg)

    asm.writeArgument(immArg.cast(memArg.operandSize))

def writeInterruptInstruction(asm, args):
    if len(args) != 1:
        raise Exception("'int' takes precisely one argument.")
    immArg = args[0].toUnsigned()
    if immArg.operandSize > size8:
        raise Exception("'int' must take an 8-bit operand.")

    asm.write([0xcd])
    asm.writeArgument(immArg.cast(size8))

def writePushPopRegisterInstruction(regOpCode, asm, arg):
    asm.write([regOpCode << 3 | arg.operandIndex])

def writePushPopInstruction(name, regOpCode, memOpCode, memReg, asm, args):
    if len(args) != 1:
        raise Exception("'" + name + "' takes precisely one argument.")

    arg = args[0]

    if arg.addressingMode == "register":
        writePushPopRegisterInstruction(regOpCode, asm, arg)
    else:
        asm.write([memOpCode, createModRM(arg.addressingMode, memReg, arg.operandIndex)])
        asm.writeArgument(arg)

def writeEnterInstruction(asm, args):
    if len(args) != 2:
        raise Exception("'enter' takes precisely two arguments.")
    if not isinstance(args[0], Instructions.ImmediateOperandBase) or not isinstance(args[1], Instructions.ImmediateOperandBase):
        raise Exception("'enter' must take two immediate arguments.")
    if args[0].operandSize > size16 or args[1].operandSize > size8:
        raise Exception("'enter' must take a 16-bit operand and an 8-bit operand.")

    asm.write([0xc8])
    asm.writeArgument(args[0].cast(size16))
    asm.writeArgument(args[1].cast(size8))

def writeRetInstruction(asm, args):
    if len(args) > 1 or (len(args) > 0 and args[0].operandSize > size16):
        raise Exception("'ret' takes at most one 16-bit operand.")

    if len(args) == 0 or args[0].operandSize == size0:
        writeSimpleInstruction("ret", [0xc3], asm, args)
    else:
        asm.write([0xc2])
        asm.writeArgument(args[0].cast(size16))

def writeTestImmediateInstruction(asm, args):
    if len(args) != 2:
        raise Exception("'test' takes precisely two operands.")
    
    (memArg, immArg) = (args[0], args[1]) if isinstance(args[1], Instructions.ImmediateOperandBase) else (args[1], args[0])

    if not isinstance(immArg, Instructions.ImmediateOperandBase) or isinstance(memArg, Instructions.ImmediateOperandBase):
        raise Exception("'test' must take precisely one immediate operand and one memory/register operand.")

    if immArg.operandSize > memArg.operandSize:
        raise Exception("The immediate operand may not be greater than the memory operand in a 'test' instruction.")

    isWord = memArg.operandSize > size8
    if memArg.operandIndex == 0 and memArg.addressingMode == "register":
        asm.write([0xa8 | int(isWord) & 0x01])
        asm.writeArgument(immArg.cast(memArg.operandSize))
    else:
        asm.write([0xf6 | int(isWord) & 0x01])
        asm.write([createModRM(memArg.addressingMode, 0, memArg.operandIndex)])
        asm.writeArgument(immArg.cast(memArg.operandSize))

def writePrefixedInstruction(prefix, instructionBuilder, asm, args):
    asm.write([prefix])
    instructionBuilder(asm, args)

def writeAmbiguousBinaryInstruction(registerInstructionBuilder, immediateInstructionBuilder, asm, args):
    if len(args) > 1 and isinstance(args[1], Instructions.ImmediateOperandBase):
        immediateInstructionBuilder(asm, args)
    else:
        registerInstructionBuilder(asm, args)

def definePrefixedInstruction(prefix, instructionBuilder):
    return lambda asm, args: writePrefixedInstruction(prefix, instructionBuilder, asm, args)

def defineSimpleInstruction(name, opCode):
    return lambda asm, args: writeSimpleInstruction(name, opCode, asm, args)

def defineBinaryInstruction(name, opCode, needCast = True):
    return lambda asm, args: writeBinaryInstruction(name, opCode, asm, args, needCast)

def defineBinaryImmediateInstruction(name, opCode):
    return lambda asm, args: writeBinaryImmediateInstruction(name, opCode, asm, args)

def defineAmbiguousInstruction(registerInstructionBuilder, immediateInstructionBuilder):
    return lambda asm, args: writeAmbiguousBinaryInstruction(registerInstructionBuilder, immediateInstructionBuilder, asm, args)

def defineReversedArgumentsInstruction(instructionBuilder):
    return lambda asm, args: instructionBuilder(asm, list(reversed(args)))

def definePushPopInstruction(name, regOpCode, memOpCode, memReg):
    return lambda asm, args: writePushPopInstruction(name, regOpCode, memOpCode, memReg, asm, args)

def defineAmbiguousBinaryInstruction(name, immOpCode, opCode = None):
    if opCode is None:
        opCode = immOpCode << 1
    binDef = defineBinaryInstruction(name, opCode)
    immDef = defineBinaryImmediateInstruction(name, immOpCode)
    return defineAmbiguousInstruction(binDef, immDef)

def defineExtendedBinaryInstruction(name, prefix, opCode, needCast = True):
    return definePrefixedInstruction(prefix, defineBinaryInstruction(name, opCode, needCast))

def writeCallInstruction(asm, args): # Sieberts code
    if len(args) != 1:
        raise Exception("'call' takes precisely one argument.")
    asm.write([0xe8])
    asm.writeArgument(args[0].makeRelative(asm.index + 4).cast(size32))
    
def writeJumpInstruction(asm, args): # tevens
    if len(args) != 1:
        raise Exception("'jmp' takes precisely one argument.")
        
    if args[0].operandSize == size8:
        asm.write([0xeb])
        asm.writeArgument(args[0].makeRelative(asm.index + 1).cast(size8))
    else:
        asm.write([0xe9])
        asm.writeArgument(args[0].makeRelative(asm.index + 4).cast(size32))

addressingModeEncodings = {
    "register" : 3,
    "memory" : 0,
    "memoryByteOffset" : 1,
    "memoryWordOffset" : 2
}

def encodeAddressingMode(mode):
    return addressingModeEncodings[mode]

instructionBuilders = {
    # This should come in handy when encoding instructions:
    #     http://pdos.csail.mit.edu/6.828/2006/readings/i386/c17.htm

    "pause" : defineSimpleInstruction("pause", [0xf3, 0x90]),
    "hlt"   : defineSimpleInstruction("hlt", [0xf4]),
    "nop"   : defineSimpleInstruction("nop", [0x90]),
    "clc"   : defineSimpleInstruction("clc", [0xf8]),
    "cld"   : defineSimpleInstruction("cld", [0xfc]),
    "cli"   : defineSimpleInstruction("cli", [0xfa]),
    "cmc"   : defineSimpleInstruction("cmc", [0xf5]),
    "clts"  : defineSimpleInstruction("clts", [0x0f, 0x06]),
    "stc"   : defineSimpleInstruction("stc", [0xf9]),
    "iret"  : defineSimpleInstruction("iret", [0xcf]),
    "iretd" : defineSimpleInstruction("iretd", [0xcf]), # Same mnemonic, apparently
    "ret"   : writeRetInstruction,
    "leave" : defineSimpleInstruction("leave", [0xc9]),
    "pusha" : defineSimpleInstruction("pusha", [0x60]),
    "popa"  : defineSimpleInstruction("popa", [0x61]),
    "enter" : writeEnterInstruction,
    "push"  : definePushPopInstruction("push", 0xa, 0xff, 0x6),
    "pop"   : definePushPopInstruction("pop", 0xb, 0x8f, 0x0),
    "int"   : writeInterruptInstruction,
    "mov"   : defineAmbiguousInstruction(defineBinaryInstruction("mov", 0x22), writeMovImmediateInstruction),
    "movsx" : defineExtendedBinaryInstruction("movsx", 0x0f, 0x2f, False),
    "movzx" : defineExtendedBinaryInstruction("movzx", 0x0f, 0x2d, False),
    "lea"   : defineReversedArgumentsInstruction(defineBinaryInstruction("lea", 0x23)),
    "add"   : defineAmbiguousBinaryInstruction("add", 0x00),
    "sub"   : defineAmbiguousBinaryInstruction("sub", 0x05),
    "and"   : defineAmbiguousBinaryInstruction("and", 0x04),
    "sbb"   : defineAmbiguousBinaryInstruction("sbb", 0x03),
    "adc"   : defineAmbiguousBinaryInstruction("adc", 0x02),
    "or"    : defineAmbiguousBinaryInstruction("or", 0x01),
    "xor"   : defineAmbiguousBinaryInstruction("xor", 0x06),
    "cmp"   : defineAmbiguousBinaryInstruction("cmp", 0x07),
    "test"  : defineAmbiguousInstruction(defineBinaryInstruction("test", 0x21), writeTestImmediateInstruction),
    "imul"  : defineExtendedBinaryInstruction("imul", 0x0f, 0x2b), # imul and idiv are *not* working properly!
    "idiv"  : defineBinaryInstruction("idiv", 0x3d),
	"call"	: writeCallInstruction,
	"jmp"	: writeJumpInstruction
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
            self.labels[str(node.name)] = self.index
        elif isinstance(node, InstructionNode):
            self.processInstruction(node)
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

        if op in instructionBuilders:
            instructionBuilders[op](self, node.argumentList.toOperands(self))
        else:
            raise ValueError('unknown opcode')