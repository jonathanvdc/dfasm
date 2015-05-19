from Parser import *
from Encoding import *

def writeSimpleInstruction(name, opCode, asm, args):
    if len(args) > 0:
        raise SyntaxError("'" + name + "' does not take any arguments.")
    asm.write(opCode)

def createModRM(mode, regIndex, memIndex):
    """ Created a MOD R/M byte. """
    return encodeAddressingMode(mode) << 6 | regIndex << 3 | memIndex

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
    regIndex = regArg.operandIndex
    memIndex = memArg.operandIndex

    opcodeByte = opCode << 2 | (int(reverseArgs) & 0x01) << 1 | int(isWord) & 0x01
    operandsByte = createModRM(memArg.addressingMode, regIndex, memIndex)

    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(memArg)

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

    opcodeByte = 0x80 | (int(shortImm) & 0x01) << 1 | int(wordReg) & 0x01
    operandsByte = createModRM(memArg.addressingMode, opCode, memArg.operandIndex)
    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(memArg)
    asm.writeArgument(immArg)

def writeMovImmediateInstruction(asm, args):
    if len(args) != 2:
        raise SyntaxError("'mov' takes precisely two arguments.")

    memArg, immArg = args[0], args[1]

    if memArg.addressingMode == "register":
        asm.write([0xb << 4 | (int(memArg.operandSize != size8) & 0x01) << 3 | memArg.operandIndex])
    else:
        asm.write([0xc6 | (int(memArg.operandSize != size8) & 0x01)])
        mode = encodeAddressingMode(memArg.addressingMode)
        asm.write([createModRM(mode, 0x00, memArg.operandIndex)])
        asm.writeArgument(memArg)

    asm.writeArgument(immArg.cast(memArg.operandSize))

def writeInterruptInstruction(asm, args):
    if len(args) != 1:
        raise SyntaxError("'int' takes precisely one argument.")
    immArg = args[0].toUnsigned()
    if immArg.operandSize > size8:
        raise SyntaxError("'int' must take an 8-bit operand.")

    asm.write([0xcd])
    asm.writeArgument(immArg.cast(size8))

def writePushPopRegisterInstruction(regOpCode, asm, arg):
    asm.write([regOpCode << 3 | arg.operandIndex])

def writePushPopInstruction(name, regOpCode, memOpCode, memReg, asm, args):
    if len(args) != 1:
        raise SyntaxError("'" + name + "' takes precisely one argument.")

    arg = args[0]

    if arg.addressingMode == "register":
        writePushPopRegisterInstruction(regOpCode, asm, arg)
    else:
        asm.write([memOpCode, createModRM(arg.addressingMode, memReg, arg.operandIndex)])
        asm.writeArgument(arg)


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

def defineBinaryInstruction(name, opCode):
    return lambda asm, args: writeBinaryInstruction(name, opCode, asm, args)

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

def defineExtendedBinaryInstruction(name, prefix, opCode):
    return definePrefixedInstruction(prefix, defineBinaryInstruction(name, opCode))
	
def writeCallInstruction(asm, args): # Sieberts code
	if len(args) != 1:
		raise SyntaxError("'call' takes precisely one argument.")
	asm.write([0xe9])
	args[0].cast(size32).writeDataTo(asm)
	
def writeJumpInstruction(asm, args): # tevens
	if len(args) != 1:
		raise SyntaxError("'jmp' takes precisely one argument.")
		
	if args[0].operandSize == size8:
		asm.write([0xeb])
		args[0].cast(size8).writeDataTo(asm)
		return
	else:
		asm.write([0xe9])
		args[0].cast(size32).writeDataTo(asm)

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
    "nop"   : defineSimpleInstruction("nop", [0x90]),
    "clc"   : defineSimpleInstruction("clc", [0xf8]),
    "stc"   : defineSimpleInstruction("stc", [0xf9]),
    "ret"   : defineSimpleInstruction("ret", [0xc3]),
    "pusha" : defineSimpleInstruction("pusha", [0x60]),
    "popa"  : defineSimpleInstruction("popa", [0x61]),
    "push"  : definePushPopInstruction("push", 0xa, 0xff, 0x6),
    "pop"   : definePushPopInstruction("pop", 0xb, 0x8f, 0x0),
    "int"   : writeInterruptInstruction,
    "mov"   : defineAmbiguousInstruction(defineBinaryInstruction("mov", 0x22), writeMovImmediateInstruction),
    "lea"   : defineReversedArgumentsInstruction(defineBinaryInstruction("lea", 0x23)),
    "add"   : defineAmbiguousBinaryInstruction("add", 0x00),
    "sub"   : defineAmbiguousBinaryInstruction("sub", 0x05),
    "and"   : defineAmbiguousBinaryInstruction("and", 0x04),
    "or"    : defineAmbiguousBinaryInstruction("or", 0x01),
    "xor"   : defineAmbiguousBinaryInstruction("xor", 0x06),
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