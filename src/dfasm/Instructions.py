from Encoding import *
import Symbols

class Register(object):
    """ Represents a processor register. """
    def __init__(self, name, index, size, isSegmentRegister):
        self.name = name
        self.index = index
        self.size = size
        self.isSegmentRegister = isSegmentRegister

    @property
    def isWord(self):
        return self.size > size8

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Register(%r, %r, %r, %r)" % (self.name, self.index, self.size, self.isSegmentRegister)

registers = {
    "eax" : Register("eax", 0, size32, False),
    "ecx" : Register("ecx", 1, size32, False),
    "edx" : Register("edx", 2, size32, False),
    "ebx" : Register("ebx", 3, size32, False),
    "esp" : Register("esp", 4, size32, False), # Note: addressing memory based on esp is not allowed.
    "ebp" : Register("ebp", 5, size32, False),
    "esi" : Register("esi", 6, size32, False),
    "edi" : Register("edi", 7, size32, False),

    "al"  : Register("al", 0, size8, False),
    "cl"  : Register("cl", 1, size8, False),
    "dl"  : Register("dl", 2, size8, False),
    "bl"  : Register("bl", 3, size8, False),
    "ah"  : Register("al", 4, size8, False),
    "ch"  : Register("cl", 5, size8, False),
    "dh"  : Register("dl", 6, size8, False),
    "bh"  : Register("bl", 7, size8, False),

    "ax"  : Register("ax", 0, size16, False),
    "cx"  : Register("cx", 1, size16, False),
    "dx"  : Register("dx", 2, size16, False),
    "bx"  : Register("bx", 3, size16, False),
    "sp"  : Register("sp", 4, size16, False),
    "bp"  : Register("bp", 5, size16, False),
    "si"  : Register("si", 6, size16, False),
    "di"  : Register("di", 7, size16, False),

    "cs"  : Register("cs", 0x2e, size16, True),
    "ss"  : Register("ss", 0x36, size16, True),
    "ds"  : Register("ds", 0x3e, size16, True),
    "es"  : Register("es", 0x26, size16, True),
    "fs"  : Register("fs", 0x64, size16, True),
    "gs"  : Register("gs", 0x65, size16, True)
}

class Operand(object):
    """ Defines a base class for instruction operands. """

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        asm.write(self.getData(asm))

    def canWrite(self):
        """ Gets a boolean value that tells whether the operand can be written
        now (True) or must be deferred (False). """
        raise NotImplementedError

    def cast(self):
        """ "Casts" this operand to match the given size, by casting its
        subexpressions. """
        raise NotImplementedError

class RegisterOperand(Operand):
    """ Defines a register operand. """
    def __init__(self, register):
        self.register = register

    @property
    def addressingMode(self):
        """ Gets the register operand's addressing mode. """
        return "register"

    @property
    def operandSize(self):
        """ Gets the operand value's size. """
        return self.register.size

    @property
    def operandIndex(self):
        """ Gets the register operand's 3-bit operand index. """
        return self.register.index

    @property
    def dataSize(self):
        """ Gets the number of bytes of data in this operand. """
        return 0

    def canWrite(self, asm):
        return True

    def getData(self, asm):
        return []

    def __str__(self):
        return str(self.register)

    def __repr__(self):
        return "RegisterOperand(%r)" % self.register

class BinaryOperand(Operand):
    """ Represents a binary pseudo-operand. The x86 ISA does not support these
    operands; they are to be used solely for the assembler's intermediate
    representation. """

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def cast(self, size):
        return BinaryOperand(self.left.cast(size), self.op, self.right.cast(size))

    def canWrite(self, asm):
        return False

    def __str__(self):
        return "%s `%s` %s" % (self.left, self.op, self.right)

    def __repr__(self):
        return "BinaryOperand(%r, %r, %r)" % (self.left, self.op, self.right)

class ImmediateOperandBase(Operand):
    """ A base class for immediate and label operands. """
    pass

class SymbolOperand(Operand):
    """ A type for operands that refer to a symbol. """
    def __init__(self, symbol, operandSize, offset, relativeOffset = None):
        self.symbol = symbol
        self.operandSize = operandSize
        self.offset = offset
        self.relativeOffset = relativeOffset

    @property
    def isRelative(self):
        """ Checks if this symbol operand is relative. """
        return self.relativeOffset is not None

    @property
    def isAbsolute(self):
        """ Checks if this symbol operand is absolute. """
        return not self.isRelative

    @property
    def dataSize(self):
        """ Gets the number of bytes of data in this operand. """
        return self.operandSize.size

    def canWrite(self, asm):
        return self.symbol.isDefined and (asm.baseOffset is not None or self.isRelative)

    def getSymbolOffset(self, asm):
        """ Gets the symbol's offset, based on the given base address. """
        if self.symbol.isExternal or (self.isAbsolute and not asm.relocateAbsolutes):
            return 0
        return self.symbol.offset + (-self.relativeOffset if self.isRelative else asm.baseOffset)

    def getData(self, asm):
        if self.isAbsolute or self.symbol.isExternal:
            asm.relocations.append(self)
        return self.operandSize.encoding(self.getSymbolOffset(asm))

    def makeRelative(self, relativeOffset):
        """ Turns this operand into a relative operand. """
        return SymbolOperand(self.symbol, self.operandSize, self.offset, relativeOffset)

    def makeAbsolute(self):
        """ Turns this operand into an absolute operand. """
        return SymbolOperand(self.symbol, self.operandSize, self.offset)

    def cast(self, size):
        return SymbolOperand(self.symbol, size, self.offset, self.relativeOffset)

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return "SymbolOperand(%r, %r, %r, %r)" % (self.symbol, self.operandSize, self.offset, self.relativeOffset)

class ImmediateOperand(ImmediateOperandBase):
    """ Represents an immediate operand. """
    def __init__(self, value, operandSize):
        self.value = value
        self.operandSize = operandSize

    def getData(self, asm):
        return self.operandSize.encoding(self.value)

    @property
    def dataSize(self):
        """ Gets the number of bytes of data in this operand. """
        return self.operandSize.size

    def canWrite(self, asm):
        return True

    def cast(self, size):
        return ImmediateOperand(self.value, size)

    def toUnsigned(self):
        return ImmediateOperand.createUnsigned(self.value)

    def makeSymbol(self, asm, offset):
        """ Turns this immediate operand into a symbol operand. """
        return SymbolOperand(asm.getSymbolAt(self.value), self.operandSize, offset)

    @staticmethod
    def createSigned(value):
        if value == 0:
            return ImmediateOperand(0, size0)
        elif -128 <= value <= 127:
            return ImmediateOperand(value, size8)
        elif -2 ** 15 <= value <= 2 ** 15 - 1:
            return ImmediateOperand(value, size16)
        else:
            return ImmediateOperand(value, size32)

    @staticmethod
    def createUnsigned(value):
        if value == 0:
            return ImmediateOperand(0, size0)
        elif 0 < value <= 255:
            return ImmediateOperand(value, size8)
        elif 0 <= value <= 2 ** 16 - 1:
            return ImmediateOperand(value, size16)
        else:
            return ImmediateOperand(value, size32)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "ImmediateOperand(%r, %r)" % (self.value, self.operandSize)

class LabelOperandBase(ImmediateOperandBase):
    """ A base class for label operands. """
    def __init__(self, labelName, operandSize):
        self.labelName = labelName
        self.operandSize = operandSize
        self.placementIndex = None

    def createOperand(self, asm):
        if self.placementIndex is None:
            self.placementIndex = asm.index
        return self.makeSymbol(asm, self.placementIndex)

    def canWrite(self, asm):
        return self.createOperand(asm).canWrite(asm)

    def makeRelative(self, offset):
        """ Turns this label operand into a relative operand. """
        return RelativeLabelOperand(offset, self.labelName, self.operandSize)

    def makeSymbol(self, asm, offset):
        """ Turns this label operand into a symbol operand. """
        raise NotImplementedError

    @property
    def dataSize(self):
        """ Gets the number of bytes of data in this operand. """
        return self.operandSize.size

    def getData(self, asm):
        return self.createOperand(asm).getData(asm)

    def __str__(self):
        return self.labelName

class RelativeLabelOperand(LabelOperandBase):
    """ Describes a relative label operand. """
    def __init__(self, offset, labelName, operandSize):
        self.offset = offset
        self.labelName = labelName
        self.operandSize = operandSize

    def makeSymbol(self, asm, offset):
        return SymbolOperand(asm.getSymbol(self.labelName), self.operandSize, offset, self.offset)

    def cast(self, size):
        return RelativeLabelOperand(self.offset, self.labelName, size)

    def __repr__(self):
        return "RelativeLabelOperand(%r, %r, %r)" % (self.offset, self.labelName, self.operandSize)

class LabelOperand(LabelOperandBase):
    """ Describes an absolute label operand. """
    def cast(self, size):
        return LabelOperand(self.labelName, size)

    def makeSymbol(self, asm, offset):
        return SymbolOperand(asm.getSymbol(self.labelName), self.operandSize, offset)

    def __repr__(self):
        return "LabelOperand(%r, %r)" % (self.labelName, self.operandSize)

class MemoryOperand(Operand):
    """ Represents a simple memory operand. """
    def __init__(self, addressRegister, displacement, operandSize):
        self.addressRegister = addressRegister
        self.displacement = displacement
        self.operandSize = operandSize

    def cast(self, size):
        return MemoryOperand(self.addressRegister, self.displacement, size)

    def canWrite(self, asm):
        return self.displacement.canWrite(asm)

    def isBasePointerPlusZero(self):
        """ Returns True if this memory operand is either [ebp] or [bp]. """
        # [ebp] does not exist; its slot is taken by [disp32].
        # [ebp + disp8] does. Instructions on [ebp] must use single-
        # byte displacement instead.
        return self.addressRegister.index == registers["bp"].index \
                and self.displacement.operandSize == size0

    @property
    def dataSize(self):
        """ Gets the number of bytes of data in this instruction. """
        if self.isBasePointerPlusZero():
            return 1
        else:
            return self.displacement.dataSize

    @property
    def addressingMode(self):
        """ Gets the register operand's addressing mode. """
        if self.displacement.operandSize == size8 or self.isBasePointerPlusZero():
            return "memoryByteOffset" # [register + disp8]
        elif self.displacement.operandSize == size0:
            return "memory" # [register]
        else:
            return "memoryWordOffset" # [register + disp32]

    @property
    def operandIndex(self):
        """ Gets the register operand's 3-bit operand index. """
        return self.addressRegister.index

    def getData(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        if self.isBasePointerPlusZero():
            return [0x00]
        else:
            return self.displacement.getData(asm)

    def __str__(self):
        if self.displacement.operandSize == size0:
            return "[%s]" % self.addressRegister
        else:
            return "[%s + %s]" % (self.addressRegister, self.displacement)

    def __repr__(self):
        return "DirectMemoryOperand(%r, %r, %r)" % (self.addressRegister, self.displacement, self.operandSize)

class SIBMemoryOperand(Operand):
    """ Represents an SIB memory operand. """
    # Encoding from:
    # http://www.c-jump.com/CIS77/CPU/x86/lecture.html#X77_0100_sib_byte_layout

    def __init__(self, baseRegister, indexRegister, indexShift, displacement, operandSize):
        self.baseRegister = baseRegister
        self.indexRegister = indexRegister
        self.indexShift = indexShift
        self.displacement = displacement
        self.operandSize = operandSize

    def canWrite(self, asm):
        return self.displacement.canWrite(asm)

    def cast(self, size):
        return SIBMemoryOperand(self.baseRegister, self.indexRegister, self.indexShift, self.displacement, size)

    @property
    def addressingMode(self):
        """ Gets the register operand's addressing mode. """
        if self.displacement.operandSize == size0: 
            return "memory" # no displacement
        elif self.displacement.operandSize == size8: 
            return "memoryByteOffset" # byte displacement
        else: 
            return "memoryWordOffset" # int displacement

    @property
    def operandIndex(self):
        """ Gets the register operand's 3-bit operand index. """
        return 4 # SIB uses operand index 4

    @property
    def dataSize(self):
        """ Gets the number of bytes of data in this instruction. """
        return 1 + self.displacement.dataSize

    def getData(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        sibVal = (self.baseRegister.index | self.indexRegister.index << 3 | self.indexShift << 6) & 0xff
        return [sibVal] + self.displacement.getData(asm)

    def __str__(self):
        return "[%s + %s << %s + %s]" % (self.baseRegister, self.indexRegister,
                                         self.indexShift, self.displacement)

    def __repr__(self):
        return "SIBMemoryOperand(%r, %r, %r, %r, %r)" % (self.baseRegister, self.indexRegister,
                                                         self.indexShift, self.displacement,
                                                         self.operandSize)