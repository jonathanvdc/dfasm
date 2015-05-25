from Parser import *
from Encoding import *
import Symbols

def writeSimpleInstruction(name, opCode, asm, args):
    if len(args) > 0:
        raise Exception("'" + name + "' does not take any arguments.")
    asm.write(opCode)

def createModRM(mode, regIndex, memIndex):
    """ Created a MOD R/M byte. """
    return encodeAddressingMode(mode) << 6 | regIndex << 3 | memIndex

def writeUnaryInstruction(name, opCode, extension, asm, args, byteOnly=False):
    if len(args) != 1:
        raise Exception("'" + name + "' takes precisely one argument.")
    arg = args[0]

    isWord = arg.operandSize > size8
    if isWord and byteOnly:
        raise Exception("'" + name ++ "' requires a byte argument.")
    argIndex = arg.operandIndex

    opcodeByte = opCode | (0x01 if isWord else 0x00)
    operandsByte = createModRM(arg.addressingMode, extension, argIndex)

    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(arg)

def writeBinaryInstruction(name, opCode, asm, args, needCast = True, reverseFlag = None):
    if len(args) != 2:
        raise Exception("'" + name + "' takes precisely two arguments.")
    reverseArgs = args[0].addressingMode != "register"
    regArg, memArg = (args[1], args[0]) if reverseArgs else (args[0], args[1])
    if reverseFlag != None:
        reverseArgs = reverseFlag

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

def makeRelativeSymbolOperand(asm, shortOffset, longOffset, arg):
    if arg.makeRelative(shortOffset).operandSize <= size8:
        return arg.makeSymbol(asm, asm.index).makeRelative(shortOffset).cast(size8)
    else:
        return arg.makeSymbol(asm, asm.index).makeRelative(longOffset).cast(size32)

def writeConditionalJumpInstruction(asm, args, name, conditionOpCode):
    if len(args) != 1 or not isinstance(args[0], Instructions.ImmediateOperandBase):
        raise Exception("'" + name + "' takes precisely one immediate operand.")

    relOp = makeRelativeSymbolOperand(asm, asm.index + 2, asm.index + 6, args[0])

    if relOp.operandSize == size8:
        asm.write([0x70 | conditionOpCode])
        asm.writeArgument(relOp)
    else:
        asm.write([0x0f, 0x80 | conditionOpCode])
        asm.writeArgument(relOp)

def writePrefixedInstruction(prefix, instructionBuilder, asm, args):
    asm.write([prefix])
    instructionBuilder(asm, args)

def writeAmbiguousBinaryInstruction(registerInstructionBuilder, immediateInstructionBuilder, asm, args):
    if len(args) > 1 and isinstance(args[1], Instructions.ImmediateOperandBase):
        immediateInstructionBuilder(asm, args)
    else:
        registerInstructionBuilder(asm, args)

def writeShiftInstruction(name, extension, asm, args):
    if len(args) != 2:
        raise Exception("'%s' takes precisely two operands." % name)

    memArg, shiftArg = args
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

def writeCallInstruction(asm, args):
    if len(args) != 1 or not isinstance(args[0], Instructions.ImmediateOperandBase):
        raise Exception("'call' takes precisely one immediate operand.")
    asm.write([0xe8])
    asm.writeArgument(args[0].makeSymbol(asm, asm.index).makeRelative(asm.index + 4).cast(size32))
    
def writeJumpInstruction(asm, args):
    if len(args) != 1 or not isinstance(args[0], Instructions.ImmediateOperandBase):
        raise Exception("'jmp' takes precisely one immediate operand.")

    relOp = makeRelativeSymbolOperand(asm, asm.index + 2, asm.index + 5, args[0])

    if relOp.operandSize == size8:
        asm.write([0xeb])
        asm.writeArgument(relOp)
    else:
        asm.write([0xe9])
        asm.writeArgument(relOp)

def definePrefixedInstruction(prefix, instructionBuilder):
    return lambda asm, args: writePrefixedInstruction(prefix, instructionBuilder, asm, args)

def defineSimpleInstruction(name, opCode):
    return lambda asm, args: writeSimpleInstruction(name, opCode, asm, args)

def defineUnaryInstruction(name, opCode, extension):
    return lambda asm, args: writeUnaryInstruction(name, opCode, extension, asm, args)

def defineSetCCInstruction(name, byte):
    def write(asm, args):
        asm.write([0x0f])
        writeUnaryInstruction(name, byte, 0, asm, args, byteOnly=True)
    return write

def defineBinaryInstruction(name, opCode, needCast = True, reverseFlag = None):
    return lambda asm, args: writeBinaryInstruction(name, opCode, asm, args, needCast, reverseFlag)

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

def defineExtendedBinaryInstruction(name, prefix, opCode, needCast = True, reverseFlag = None):
    return definePrefixedInstruction(prefix, defineBinaryInstruction(name, opCode, needCast, reverseFlag))

def defineConditionalJumpInstruction(name, conditionOpCode):
    return lambda asm, args: writeConditionalJumpInstruction(asm, args, name, conditionOpCode)

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
    "std"   : defineSimpleInstruction("std", [0xfd]),
    "sti"   : defineSimpleInstruction("sti", [0xfb]),
    "sahf"  : defineSimpleInstruction("sahf", [0x9e]),
    "lahf"  : defineSimpleInstruction("lahf", [0x9f]),
    "lock"  : defineSimpleInstruction("lock", [0xf0]),
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
    "not"   : defineUnaryInstruction("not", 0xf6, 2),
    "neg"   : defineUnaryInstruction("neg", 0xf6, 3),
    "inc"   : defineUnaryInstruction("inc", 0xfe, 0),
    "dec"   : defineUnaryInstruction("dec", 0xfe, 1),
    "seta"  : defineSetCCInstruction("seta",  0x97),
    "setae" : defineSetCCInstruction("setae", 0x93),
    "setb"  : defineSetCCInstruction("setb",  0x92),
    "setbe" : defineSetCCInstruction("setbe", 0x96),
    "setc"  : defineSetCCInstruction("setc",  0x92),
    "sete"  : defineSetCCInstruction("sete",  0x94),
    "setg"  : defineSetCCInstruction("setg",  0x9f),
    "setge" : defineSetCCInstruction("setge", 0x9d),
    "setl"  : defineSetCCInstruction("setl",  0x9c),
    "setle" : defineSetCCInstruction("setle", 0x9e),
    "setna" : defineSetCCInstruction("setna", 0x96),
    "setna" : defineSetCCInstruction("setna", 0x92),
    "setnb" : defineSetCCInstruction("setnb", 0x93),
    "setnb" : defineSetCCInstruction("setnb", 0x97),
    "setnc" : defineSetCCInstruction("setnc", 0x93),
    "setne" : defineSetCCInstruction("setne", 0x95),
    "setng" : defineSetCCInstruction("setng", 0x9e),
    "setng" : defineSetCCInstruction("setng", 0x9c),
    "setnl" : defineSetCCInstruction("setnl", 0x9d),
    "setnl" : defineSetCCInstruction("setnl", 0x9f),
    "setno" : defineSetCCInstruction("setno", 0x91),
    "setnp" : defineSetCCInstruction("setnp", 0x9b),
    "setns" : defineSetCCInstruction("setns", 0x99),
    "setnz" : defineSetCCInstruction("setnz", 0x95),
    "seto"  : defineSetCCInstruction("seto",  0x90),
    "setp"  : defineSetCCInstruction("setp",  0x9a),
    "setpe" : defineSetCCInstruction("setpe", 0x9a),
    "setpo" : defineSetCCInstruction("setpo", 0x9b),
    "sets"  : defineSetCCInstruction("sets",  0x98),
    "setz"  : defineSetCCInstruction("setz",  0x94),
    "add"   : defineAmbiguousBinaryInstruction("add", 0x00),
    "sub"   : defineAmbiguousBinaryInstruction("sub", 0x05),
    "and"   : defineAmbiguousBinaryInstruction("and", 0x04),
    "sbb"   : defineAmbiguousBinaryInstruction("sbb", 0x03),
    "adc"   : defineAmbiguousBinaryInstruction("adc", 0x02),
    "or"    : defineAmbiguousBinaryInstruction("or", 0x01),
    "xor"   : defineAmbiguousBinaryInstruction("xor", 0x06),
    "cmp"   : defineAmbiguousBinaryInstruction("cmp", 0x07),
    "test"  : defineAmbiguousInstruction(defineBinaryInstruction("test", 0x21, True, True), writeTestImmediateInstruction),
    "xchg"  : defineBinaryInstruction("xchg", 0x21, True, False), # xchg conveniently overlaps with test
    "imul"  : defineExtendedBinaryInstruction("imul", 0x0f, 0x2b), # imul and idiv are *not* working properly!
    "idiv"  : defineBinaryInstruction("idiv", 0x3d),
	"call"	: writeCallInstruction,
	"jmp"	: writeJumpInstruction,
    # Lots of these conditional jump mnemonics are synonyms.
    "ja"    : defineConditionalJumpInstruction("ja", 0x7),    # Jump if above (CF == 0 && ZF == 0)
    "jae"   : defineConditionalJumpInstruction("jae", 0x3),   # Jump if above or equal (CF == 0)
    "jb"    : defineConditionalJumpInstruction("jb", 0x2),    # Jump if below (CF == 1)
    "jbe"   : defineConditionalJumpInstruction("jbe", 0x6),   # Jump if below or equal (CF == 1 || ZF == 1)
    "jc"    : defineConditionalJumpInstruction("jc", 0x2),    # Jump if carry (CF == 1)
    "je"    : defineConditionalJumpInstruction("je", 0x4),    # Jump if equal (ZF == 1)
    "jz"    : defineConditionalJumpInstruction("jz", 0x4),    # Jump if zero (ZF == 1)
    "jg"    : defineConditionalJumpInstruction("jg", 0xf),    # Jump if greater (ZF == 0 && SF == OF)
    "jge"   : defineConditionalJumpInstruction("jge", 0xd),   # Jump if greater or equal (SF == OF)
    "jl"    : defineConditionalJumpInstruction("jl", 0xc),    # Jump if less (SF != OF)
    "jle"   : defineConditionalJumpInstruction("jle", 0xe),   # Jump if less or equal (ZF == 1 && SF != OF)
    "jna"   : defineConditionalJumpInstruction("jna", 0x6),   # Jump if not above (CF == 1 || ZF == 1)
    "jnae"  : defineConditionalJumpInstruction("jnae", 0x2),  # Jump if not above or equal (CF == 1)
    "jnb"   : defineConditionalJumpInstruction("jnb", 0x3),   # Jump if not below (CF == 0)
    "jnbe"  : defineConditionalJumpInstruction("jnbe", 0x7),  # Jump if not below or equal (CF == 0 && ZF == 0)
    "jnc"   : defineConditionalJumpInstruction("jnc", 0x3),   # Jump if not carry (CF == 0)
    "jne"   : defineConditionalJumpInstruction("jne", 0x5),   # Jump if not equal (ZF == 0)
    "jng"   : defineConditionalJumpInstruction("jng", 0xe),   # Jump if not greater (ZF == 1 || SF != OF)
    "jnge"  : defineConditionalJumpInstruction("jnge", 0xc),  # Jump if not greater or equal (SF != OF)
    "jnl"   : defineConditionalJumpInstruction("jnl", 0xd),   # Jump if not less (SF == OF)
    "jnle"  : defineConditionalJumpInstruction("jnle", 0xf),  # Jump if not less or equal (ZF == 0 && SF == OF)
    "jno"   : defineConditionalJumpInstruction("jno", 0x1),   # Jump if not overflow (OF == 1)
    "jnp"   : defineConditionalJumpInstruction("jnp", 0xb),   # Jump if not parity (PF == 0)
    "jns"   : defineConditionalJumpInstruction("jns", 0x9),   # Jump if not sign (SF == 0)
    "jnz"   : defineConditionalJumpInstruction("jnz", 0x5),   # Jump if not zero (ZF == 0)
    "jo"    : defineConditionalJumpInstruction("jo", 0x0),    # Jump if overflow (OF == 1)
    "jp"    : defineConditionalJumpInstruction("jp", 0xa),    # Jump if parity (PF == 1)
    "jpe"   : defineConditionalJumpInstruction("jpe", 0xa),   # Jump if parity even (PF == 1)
    "jpo"   : defineConditionalJumpInstruction("jpo", 0xb),   # Jump if parity odd (PF == 0)
    "js"    : defineConditionalJumpInstruction("js", 0x8),    # Jump if sign (SF == 1)
    "jz"    : defineConditionalJumpInstruction("jz", 0x4),    # Jump if zero (ZF == 1)
    # TODO: the literal entirety of x86.
}

class Assembler(object):
    """ Converts a list of instructions and labels to bytecode. """

    def __init__(self, baseOffset = None, relocateAbsolutes = True):
        # A list of byte values representing the bytecode.
        self.code = []
        self.baseOffset = baseOffset # The base offset is absolutely necessary for absolute things,
                                     # but we may choose to provide it later on.

        self.relocateAbsolutes = relocateAbsolutes # This boolean value tells symbol operands whether they should try
                                                   # to fix up absolute offsets themselves, or report a pseudo-offset of 0,
                                                   # making it the linker's problem.

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

        if op in instructionBuilders:
            instructionBuilders[op](self, node.argumentList.toOperands(self))
        else:
            raise ValueError('unknown opcode')