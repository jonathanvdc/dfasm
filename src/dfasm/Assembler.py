from Parser import *
from Encoding import *
import Symbols

builders = {}

############################################################
### Simple (zero-argument) instructions
############################################################

def writeSimpleInstruction(name, opCode, asm, args):
    if len(args) > 0:
        raise ValueError("'%s' does not take any arguments." % name)
    asm.write(opCode)

def defineSimpleInstruction(name, opCode):
    return lambda asm, args: writeSimpleInstruction(name, opCode, asm, args)

builders["pause"] = defineSimpleInstruction("pause", [0xf3, 0x90])
builders["hlt"]   = defineSimpleInstruction("hlt",   [0xf4])
builders["nop"]   = defineSimpleInstruction("nop",   [0x90])
builders["clc"]   = defineSimpleInstruction("clc",   [0xf8])
builders["cld"]   = defineSimpleInstruction("cld",   [0xfc])
builders["cli"]   = defineSimpleInstruction("cli",   [0xfa])
builders["cmc"]   = defineSimpleInstruction("cmc",   [0xf5])
builders["clts"]  = defineSimpleInstruction("clts",  [0x0f, 0x06])
builders["stc"]   = defineSimpleInstruction("stc",   [0xf9])
builders["std"]   = defineSimpleInstruction("std",   [0xfd])
builders["sti"]   = defineSimpleInstruction("sti",   [0xfb])
builders["sahf"]  = defineSimpleInstruction("sahf",  [0x9e])
builders["lahf"]  = defineSimpleInstruction("lahf",  [0x9f])
builders["lock"]  = defineSimpleInstruction("lock",  [0xf0])
builders["iret"]  = defineSimpleInstruction("iret",  [0xcf])
builders["iretd"] = defineSimpleInstruction("iretd", [0xcf])
builders["leave"] = defineSimpleInstruction("leave", [0xc9])
builders["pusha"] = defineSimpleInstruction("pusha", [0x60])
builders["popa"]  = defineSimpleInstruction("popa",  [0x61])

############################################################
### Unary instructions
############################################################

addressingModeEncodings = {
    "memory" : 0,
    "memoryByteOffset" : 1,
    "memoryWordOffset" : 2,
    "register" : 3,
}

def encodeAddressingMode(mode):
    return addressingModeEncodings[mode]

def createModRM(mode, regIndex, memIndex):
    """ Created a MOD R/M byte. """
    return encodeAddressingMode(mode) << 6 | regIndex << 3 | memIndex

def writeUnaryInstruction(name, opCode, extension, asm, args, byteOnly=False):
    if len(args) != 1:
        raise ValueError("'%s' takes precisely one argument." % name)
    arg = args[0]

    isWord = arg.operandSize > size8
    if isWord and byteOnly:
        raise ValueError("'%s' requires a byte argument." % name)
    if isinstance(arg, Instructions.ImmediateOperandBase) and byteOnly:
        raise ValueError("'%s' requires a register argument." % name)
    argIndex = arg.operandIndex

    opcodeByte = opCode | (0x01 if isWord else 0x00)
    operandsByte = createModRM(arg.addressingMode, extension, argIndex)

    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(arg)

def defineUnaryInstruction(name, opCode, extension):
    return lambda asm, args: writeUnaryInstruction(name, opCode, extension, asm, args)

builders["not"]  = defineUnaryInstruction("not",  0xf6, 2)
builders["neg"]  = defineUnaryInstruction("neg",  0xf6, 3)
builders["inc"]  = defineUnaryInstruction("inc",  0xfe, 0)
builders["dec"]  = defineUnaryInstruction("dec",  0xfe, 1)
builders["mul"]  = defineUnaryInstruction("mul",  0xf6, 4)
builders["div"]  = defineUnaryInstruction("div",  0xf6, 6)
builders["idiv"] = defineUnaryInstruction("idiv", 0xf6, 7)

############################################################
### setCC instructions
############################################################

def writePrefixedInstruction(prefix, instructionBuilder, asm, args):
    asm.write([prefix])
    instructionBuilder(asm, args)

def definePrefixedInstruction(prefix, instructionBuilder):
    return lambda asm, args: writePrefixedInstruction(prefix, instructionBuilder, asm, args)

def defineSetCCInstruction(name, byte):
    def write(asm, args):
        asm.write([0x0f])
        writeUnaryInstruction(name, byte, 0, asm, args, byteOnly=True)
    return write

builders["seto"]  = defineSetCCInstruction("seto",  0x90)
builders["setno"] = defineSetCCInstruction("setno", 0x91)
builders["setb"]  = defineSetCCInstruction("setb",  0x92)
builders["setc"]  = defineSetCCInstruction("setc",  0x92)
builders["setna"] = defineSetCCInstruction("setna", 0x92)
builders["setae"] = defineSetCCInstruction("setae", 0x93)
builders["setnb"] = defineSetCCInstruction("setnb", 0x93)
builders["setnc"] = defineSetCCInstruction("setnc", 0x93)
builders["sete"]  = defineSetCCInstruction("sete",  0x94)
builders["setz"]  = defineSetCCInstruction("setz",  0x94)
builders["setne"] = defineSetCCInstruction("setne", 0x95)
builders["setnz"] = defineSetCCInstruction("setnz", 0x95)
builders["setbe"] = defineSetCCInstruction("setbe", 0x96)
builders["setna"] = defineSetCCInstruction("setna", 0x96)
builders["seta"]  = defineSetCCInstruction("seta",  0x97)
builders["setnb"] = defineSetCCInstruction("setnb", 0x97)
builders["sets"]  = defineSetCCInstruction("sets",  0x98)
builders["setns"] = defineSetCCInstruction("setns", 0x99)
builders["setp"]  = defineSetCCInstruction("setp",  0x9a)
builders["setpe"] = defineSetCCInstruction("setpe", 0x9a)
builders["setnp"] = defineSetCCInstruction("setnp", 0x9b)
builders["setpo"] = defineSetCCInstruction("setpo", 0x9b)
builders["setl"]  = defineSetCCInstruction("setl",  0x9c)
builders["setng"] = defineSetCCInstruction("setng", 0x9c)
builders["setge"] = defineSetCCInstruction("setge", 0x9d)
builders["setnl"] = defineSetCCInstruction("setnl", 0x9d)
builders["setle"] = defineSetCCInstruction("setle", 0x9e)
builders["setng"] = defineSetCCInstruction("setng", 0x9e)
builders["setg"]  = defineSetCCInstruction("setg",  0x9f)
builders["setnl"] = defineSetCCInstruction("setnl", 0x9f)

############################################################
### Binary instructions
############################################################

def writeBinaryInstruction(name, opCode, asm, args, needCast = True, reverseFlag = None):
    if len(args) != 2:
        raise ValueError("'%s' takes precisely two arguments." % name)
    reverseArgs = args[0].addressingMode != "register"
    regArg, memArg = (args[1], args[0]) if reverseArgs else (args[0], args[1])
    if reverseFlag != None:
        reverseArgs = reverseFlag

    if regArg.addressingMode != "register":
        raise ValueError("'%s' must take at least one register operand." % name)

    if needCast and memArg.operandSize != regArg.operandSize:
        # Cast if necessary
        memArg = memArg.cast(regArg.operandSize)

    isWord = memArg.operandSize > size8
    regIndex = regArg.operandIndex
    memIndex = memArg.operandIndex

    opcodeByte = opCode << 2 | (int(not reverseArgs) & 0x01) << 1 | int(isWord) & 0x01
    operandsByte = createModRM(memArg.addressingMode, regIndex, memIndex)

    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(memArg)

def defineBinaryInstruction(name, opCode, needCast = True, reverseFlag = None):
    return lambda asm, args: writeBinaryInstruction(name, opCode, asm, args, needCast, reverseFlag)

def defineExtendedBinaryInstruction(name, prefix, opCode, needCast = True, reverseFlag = None):
    return definePrefixedInstruction(prefix, defineBinaryInstruction(name, opCode, needCast, reverseFlag))

def writeBinaryImmediateInstruction(name, opCode, asm, args):
    if len(args) != 2:
        raise ValueError("'%s' takes precisely two arguments." % name)

    memArg, immArg = args[0], args[1]

    wordReg = memArg.operandSize > size8

    if immArg.operandSize == size0:
        immArg = immArg.cast(size8)
    elif immArg.operandSize != size8:
        if not wordReg:
            raise ValueError("Cannot use immediate larger than 8 bits (%s) "
                             "with 8-bit register %s" % (immArg, memArg))
        immArg = immArg.cast(memArg.operandSize)
        
    shortImm = immArg.operandSize != memArg.operandSize

    opcodeByte = 0x80 | (int(shortImm) & 0x01) << 1 | int(wordReg) & 0x01
    operandsByte = createModRM(memArg.addressingMode, opCode, memArg.operandIndex)
    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(memArg)
    asm.writeArgument(immArg)

def defineBinaryImmediateInstruction(name, opCode):
    return lambda asm, args: writeBinaryImmediateInstruction(name, opCode, asm, args)

builders["xchg"]  = defineBinaryInstruction("xchg", 0x21, True, False)
builders["movsx"] = defineExtendedBinaryInstruction("movsx", 0x0f, 0x2f, False)
builders["movzx"] = defineExtendedBinaryInstruction("movzx", 0x0f, 0x2d, False)

def defineReversedArgumentsInstruction(instructionBuilder):
    return lambda asm, args: instructionBuilder(asm, list(reversed(args)))

builders["lea"] = defineReversedArgumentsInstruction(
                      defineBinaryInstruction("lea", 0x23))

############################################################
### Ambiguous binary instructions
############################################################

def defineAmbiguousInstruction(registerInstructionBuilder, immediateInstructionBuilder):
    return lambda asm, args: writeAmbiguousBinaryInstruction(registerInstructionBuilder,
                                                             immediateInstructionBuilder,
                                                             asm, args)

def writeAmbiguousBinaryInstruction(registerInstructionBuilder, immediateInstructionBuilder, asm, args):
    if len(args) > 1 and isinstance(args[1], Instructions.ImmediateOperandBase):
        immediateInstructionBuilder(asm, args)
    else:
        registerInstructionBuilder(asm, args)

def defineAmbiguousBinaryInstruction(name, immOpCode, opCode = None):
    if opCode is None:
        opCode = immOpCode << 1
    binDef = defineBinaryInstruction(name, opCode)
    immDef = defineBinaryImmediateInstruction(name, immOpCode)
    return defineAmbiguousInstruction(binDef, immDef)

builders["add"]   = defineAmbiguousBinaryInstruction("add", 0x00)
builders["or"]    = defineAmbiguousBinaryInstruction("or",  0x01)
builders["adc"]   = defineAmbiguousBinaryInstruction("adc", 0x02)
builders["sbb"]   = defineAmbiguousBinaryInstruction("sbb", 0x03)
builders["and"]   = defineAmbiguousBinaryInstruction("and", 0x04)
builders["sub"]   = defineAmbiguousBinaryInstruction("sub", 0x05)
builders["xor"]   = defineAmbiguousBinaryInstruction("xor", 0x06)
builders["cmp"]   = defineAmbiguousBinaryInstruction("cmp", 0x07)

############################################################
### Shift instructions
############################################################

def writeShiftInstruction(name, extension, asm, args):
    if len(args) != 2:
        raise ValueError("'%s' takes precisely two operands." % name)

    memArg, shiftArg = args
    wordReg = memArg.operandSize > size8
    modRM = createModRM(memArg.addressingMode, extension, memArg.operandIndex)

    if isinstance(shiftArg, Instructions.ImmediateOperandBase):
        if shiftArg.operandSize > size8:
            raise ValueError("The immediate argument to a shift instruction cannot be larger than a byte.")
        v = shiftArg.value & 31
        if v == 1:
            asm.write([0xD1 if wordReg else 0xD0, modRM])
        else:
            asm.write([0xC1 if wordReg else 0xC0, modRM, v])
    elif shiftArg is registers["cl"]:
        asm.write([0xD3 if wordReg else 0xD2, modRM])
    else:
        raise ValueError("The second argument to a shift instruction must be an "
                        "immediate byte or the register CL.")
    asm.writeArgument(memArg)

def defineShiftInstruction(name, extension):
    return lambda asm, args: writeShiftInstruction(name, extension, asm, args)

builders["sal"]   = defineShiftInstruction("sal", 4)
builders["sar"]   = defineShiftInstruction("sar", 7)
builders["shl"]   = defineShiftInstruction("shl", 4)
builders["shr"]   = defineShiftInstruction("shr", 5)

############################################################
### Jump instructions
############################################################

def makeRelativeSymbolOperand(asm, shortOffset, longOffset, arg):
    if arg.makeRelative(shortOffset).operandSize <= size8:
        return arg.makeSymbol(asm, asm.index).makeRelative(shortOffset).cast(size8)
    else:
        return arg.makeSymbol(asm, asm.index).makeRelative(longOffset).cast(size32)

def writeCallInstruction(asm, args):
    if len(args) != 1 or not isinstance(args[0], Instructions.ImmediateOperandBase):
        raise ValueError("'call' takes precisely one immediate operand.")
    asm.write([0xe8])
    asm.writeArgument(args[0].makeSymbol(asm, asm.index).makeRelative(asm.index + 4).cast(size32))

builders["call"] = writeCallInstruction
    
def writeJumpInstruction(asm, args):
    if len(args) != 1 or not isinstance(args[0], Instructions.ImmediateOperandBase):
        raise ValueError("'jmp' takes precisely one immediate operand.")

    relOp = makeRelativeSymbolOperand(asm, asm.index + 2, asm.index + 5, args[0])

    if relOp.operandSize == size8:
        asm.write([0xeb])
        asm.writeArgument(relOp)
    else:
        asm.write([0xe9])
        asm.writeArgument(relOp)

builders["jmp"]  = writeJumpInstruction

############################################################
### Conditional jump instructions
############################################################
    
def writeConditionalJumpInstruction(asm, args, name, conditionOpCode):
    if len(args) != 1 or not isinstance(args[0], Instructions.ImmediateOperandBase):
        raise ValueError("'%s' takes precisely one immediate operand." % name)

    relOp = makeRelativeSymbolOperand(asm, asm.index + 2, asm.index + 6, args[0])

    if relOp.operandSize == size8:
        asm.write([0x70 | conditionOpCode])
        asm.writeArgument(relOp)
    else:
        asm.write([0x0f, 0x80 | conditionOpCode])
        asm.writeArgument(relOp)

def defineConditionalJumpInstruction(name, conditionOpCode):
    return lambda asm, args: writeConditionalJumpInstruction(asm, args, name, conditionOpCode)

builders["jo"]   = defineConditionalJumpInstruction("jo",   0x0)
builders["jno"]  = defineConditionalJumpInstruction("jno",  0x1)
builders["jb"]   = defineConditionalJumpInstruction("jb",   0x2)
builders["jc"]   = defineConditionalJumpInstruction("jc",   0x2)
builders["jnae"] = defineConditionalJumpInstruction("jnae", 0x2)
builders["jae"]  = defineConditionalJumpInstruction("jae",  0x3)
builders["jnb"]  = defineConditionalJumpInstruction("jnb",  0x3)
builders["jnc"]  = defineConditionalJumpInstruction("jnc",  0x3)
builders["je"]   = defineConditionalJumpInstruction("je",   0x4)
builders["jz"]   = defineConditionalJumpInstruction("jz",   0x4)
builders["jnz"]  = defineConditionalJumpInstruction("jnz",  0x5)
builders["jne"]  = defineConditionalJumpInstruction("jne",  0x5)
builders["jbe"]  = defineConditionalJumpInstruction("jbe",  0x6)
builders["jna"]  = defineConditionalJumpInstruction("jna",  0x6)
builders["ja"]   = defineConditionalJumpInstruction("ja",   0x7)
builders["jnbe"] = defineConditionalJumpInstruction("jnbe", 0x7)
builders["js"]   = defineConditionalJumpInstruction("js",   0x8)
builders["jns"]  = defineConditionalJumpInstruction("jns",  0x9)
builders["jp"]   = defineConditionalJumpInstruction("jp",   0xa)
builders["jpe"]  = defineConditionalJumpInstruction("jpe",  0xa)
builders["jnp"]  = defineConditionalJumpInstruction("jnp",  0xb)
builders["jpo"]  = defineConditionalJumpInstruction("jpo",  0xb)
builders["jl"]   = defineConditionalJumpInstruction("jl",   0xc)
builders["jnge"] = defineConditionalJumpInstruction("jnge", 0xc)
builders["jge"]  = defineConditionalJumpInstruction("jge",  0xd)
builders["jnl"]  = defineConditionalJumpInstruction("jnl",  0xd)
builders["jle"]  = defineConditionalJumpInstruction("jle",  0xe)
builders["jng"]  = defineConditionalJumpInstruction("jng",  0xe)
builders["jg"]   = defineConditionalJumpInstruction("jg",   0xf)
builders["jnle"] = defineConditionalJumpInstruction("jnle", 0xf)

############################################################
### Push/pop instructions
############################################################

def writePushPopRegisterInstruction(regOpCode, asm, arg):
    asm.write([regOpCode << 3 | arg.operandIndex])

def writePushPopInstruction(name, regOpCode, memOpCode, memReg, asm, args):
    if len(args) != 1:
        raise ValueError("'%s' takes precisely one argument." % name)

    arg = args[0]

    if arg.addressingMode == "register":
        writePushPopRegisterInstruction(regOpCode, asm, arg)
    else:
        asm.write([memOpCode, createModRM(arg.addressingMode, memReg, arg.operandIndex)])
        asm.writeArgument(arg)

def definePushPopInstruction(name, regOpCode, memOpCode, memReg):
    return lambda asm, args: writePushPopInstruction(name, regOpCode, memOpCode, memReg, asm, args)

builders["push"]  = definePushPopInstruction("push", 0xa, 0xff, 0x6)
builders["pop"]   = definePushPopInstruction("pop", 0xb, 0x8f, 0x0)

############################################################
### Move instruction
############################################################

def writeMovImmediateInstruction(asm, args):
    if len(args) != 2:
        raise ValueError("'mov' takes precisely two arguments.")

    memArg, immArg = args[0], args[1]

    if memArg.addressingMode == "register":
        asm.write([0xb << 4 | (int(memArg.operandSize != size8) & 0x01) << 3 | memArg.operandIndex])
    else:
        asm.write([0xc6 | (int(memArg.operandSize != size8) & 0x01)])
        asm.write([createModRM(memArg.addressingMode, 0x00, memArg.operandIndex)])
        asm.writeArgument(memArg)

    asm.writeArgument(immArg.cast(memArg.operandSize))

builders["mov"] = defineAmbiguousInstruction(
                      defineBinaryInstruction("mov", 0x22),
                      writeMovImmediateInstruction)

############################################################
### Interrupt instruction
############################################################

def writeInterruptInstruction(asm, args):
    if len(args) != 1:
        raise ValueError("'int' takes precisely one argument.")
    immArg = args[0].toUnsigned()
    if immArg.operandSize > size8:
        raise ValueError("'int' must take an 8-bit operand.")

    asm.write([0xcd])
    asm.writeArgument(immArg.cast(size8))

builders["int"]   = writeInterruptInstruction

############################################################
### Test instruction
############################################################

def writeTestImmediateInstruction(asm, args):
    if len(args) != 2:
        raise ValueError("'test' takes precisely two operands.")
    
    isImm = lambda x: isinstance(x, Instructions.ImmediateOperandBase)

    immArg, memArg = args
    if isImm(memArg):
        immArg, memArg = memArg, immArg

    if not isImm(immArg) or isImm(memArg):
        raise ValueError("'test' must take precisely one immediate operand and one memory/register operand.")

    if immArg.operandSize > memArg.operandSize:
        raise ValueError("The immediate operand may not be greater than the memory operand in a 'test' instruction.")

    isWord = memArg.operandSize > size8
    if memArg.operandIndex == 0 and memArg.addressingMode == "register":
        asm.write([0xa8 | int(isWord) & 0x01])
        asm.writeArgument(immArg.cast(memArg.operandSize))
    else:
        asm.write([0xf6 | int(isWord) & 0x01])
        asm.write([createModRM(memArg.addressingMode, 0, memArg.operandIndex)])
        asm.writeArgument(immArg.cast(memArg.operandSize))

builders["test"]  = defineAmbiguousInstruction(
                        defineBinaryInstruction("test", 0x21, True, True),
                        writeTestImmediateInstruction)

############################################################
### Enter (= build stack frame) instruction
############################################################

def writeEnterInstruction(asm, args):
    if len(args) != 2:
        raise ValueError("'enter' takes precisely two arguments.")
    if not all(isinstance(arg, Instructions.ImmediateOperandBase) for arg in args):
        raise ValueError("'enter' must take two immediate arguments.")
    if args[0].operandSize > size16 or args[1].operandSize > size8:
        raise ValueError("'enter' must take a 16-bit operand and an 8-bit operand.")

    asm.write([0xc8])
    asm.writeArgument(args[0].cast(size16))
    asm.writeArgument(args[1].cast(size8))

builders["enter"] = writeEnterInstruction

############################################################
### Return instruction
############################################################

def writeRetInstruction(asm, args):
    if len(args) > 1 or (len(args) > 0 and args[0].operandSize > size16):
        raise ValueError("'ret' takes at most one 16-bit operand.")

    if len(args) == 0 or args[0].operandSize == size0:
        writeSimpleInstruction("ret", [0xc3], asm, args)
    else:
        asm.write([0xc2])
        asm.writeArgument(args[0].cast(size16))

builders["ret"]   = writeRetInstruction

############################################################
### Immediate multiply instruction
############################################################

def writeThreeOpImmediateInstruction(name, opCode, asm, args):
    if len(args) != 2 and len(args) != 3:
        raise ValueError("'%s' takes either two or three arguments." % name)

    if len(args) == 2:
        args = [args[0], args[0], args[1]] # transform `imul eax,      10`
                                           # into      `imul eax, eax, 10`

    regArg, memArg, immArg = args

    if regArg.addressingMode != "register":
        raise ValueError("'%s' instruction must have a register operand "
                         "as its first argument." % name)

    if regArg.operandSize != memArg.operandSize:
        if memArg.addressingMode == "register":
            raise ValueError("Register size mismatch ('%s' and '%s') in '%s' "
                             "instruction." % (regArg, memArg, name))
        else:
            memArg = memArg.cast(regArg.operandSize)

    wordReg = memArg.operandSize > size8

    if immArg.operandSize == size0:
        immArg = immArg.cast(size8)
    elif immArg.operandSize != size8:
        if not wordReg:
            raise ValueError("Cannot use an immediate larger than 8 bits (%s) "
                             "with 8-bit register '%s'." % (immArg, regArg))
        immArg = immArg.cast(memArg.operandSize)
        
    shortImm = immArg.operandSize != memArg.operandSize

    opcodeByte = opCode << 2 | (int(shortImm) & 0x01) << 1 | int(wordReg) & 0x01
    operandsByte = createModRM(memArg.addressingMode, regArg.operandIndex, memArg.operandIndex)
    asm.write([opcodeByte, operandsByte])
    asm.writeArgument(memArg)
    asm.writeArgument(immArg)

def defineThreeOpImmediateInstruction(name, opCode):
    return lambda asm, args: writeThreeOpImmediateInstruction(name, opCode, asm, args)

def defineAmbiguousArgumentCountInstruction(instructionBuilderDict):
    return lambda asm, args: instructionBuilderDict[len(args)](asm, args)

builders["imul"] = defineAmbiguousArgumentCountInstruction({
                     1 : defineUnaryInstruction("imul", 0xF6, 5),
                     2 : defineAmbiguousInstruction(
                           defineExtendedBinaryInstruction("imul", 0x0f, 0x2b),
                           defineThreeOpImmediateInstruction("imul", 0x6B >> 2)),
                     3 : defineThreeOpImmediateInstruction("imul", 0x6B >> 2),
                   })

############################################################
### Assembler class
############################################################

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