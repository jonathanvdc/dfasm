from Encoding import *

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

    "cs"  : Register("cs", 0x2E, size16, True),
    "ss"  : Register("ss", 0x36, size16, True),
    "ds"  : Register("ds", 0x3E, size16, True),
    "es"  : Register("es", 0x26, size16, True),
    "fs"  : Register("fs", 0x64, size16, True),
    "gs"  : Register("gs", 0x65, size16, True)
}

class RegisterOperand(object):
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

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        pass

    def __str__(self):
        return str(self.register)

    def __repr__(self):
        return "RegisterOperand(%r)" % self.register

class BinaryOperand(object):
    """ Represents a binary pseudo-operand.
        The x86 ISA does not support these operands.
        They are to be used soley for the assembler's intermediate representation. """

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def cast(self, size):
        """ "Casts" this operand to match the given size. """
        return BinaryOperand(self.left.cast(size), self.op, self.right.cast(size))

    def __str__(self):
        return str(self.left) + " `" + self.op + "` " + str(self.right)

    def __repr__(self):
        return "Represents(%r, %r, %r)" % (self.left, self.op, self.right)

class ImmediateOperand(object):
    """ Represents an immediate operand. """
    def __init__(self, value, operandSize):
        self.value = value
        self.operandSize = operandSize

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        asm.write(self.operandSize.encoding(self.value))

    def cast(self, size):
        """ "Casts" this operand to match the given size. """
        return ImmediateOperand(self.value, size)

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

class MemoryOperand(object):
    """ Represents a simple memory operand. """
    def __init__(self, addressRegister, displacement, operandSize):
        self.addressRegister = addressRegister
        self.displacement = displacement
        self.operandSize = operandSize

    def cast(self, size):
        """ "Casts" this operand to match the given size. """
        return MemoryOperand(self.addressRegister, self.displacement, size)

    @property
    def addressingMode(self):
        """ Gets the register operand's addressing mode. """
        if self.displacement.operandSize == size8 or (self.addressRegister.index == 5 and self.displacement.operandSize == size0):
            return "memoryByteOffset" # [register + disp8]
            # Note: [ebp] does not exist (its slot is taken by [disp32]. [ebp + disp8] does.
        elif self.displacement.operandSize == size0:
            return "memory" # [register]
        else:
            return "memoryWordOffset" # [register + disp32]

    @property
    def operandIndex(self):
        """ Gets the register operand's 3-bit operand index. """
        return self.addressRegister.index

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        if self.addressRegister.index == 5 and self.displacement.operandSize == size0:
            asm.write([0x00])
        else:
            self.displacement.writeDataTo(asm)

    def __str__(self):
        if self.displacement.operandSize == size0:
            return "[" + str(self.addressRegister) + "]"
        else:
            return "[" + str(self.addressRegister) + " + " + str(self.displacement) + "]"

    def __repr__(self):
        return "DirectMemoryOperand(%r, %r, %r)" % (self.addressRegister, self.displacement, self.operandSize)

class SIBMemoryOperand(object):
    """ Represents an SIB memory operand. """
    # Encoding from:
    # http://www.c-jump.com/CIS77/CPU/x86/lecture.html#X77_0100_sib_byte_layout

    def __init__(self, baseRegister, indexRegister, indexShift, displacement, operandSize):
        self.baseRegister = baseRegister
        self.indexRegister = indexRegister
        self.indexShift = indexShift
        self.displacement = displacement
        self.operandSize = operandSize

    def cast(self, size):
        """ "Casts" this operand to match the given size. """
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

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        sibVal = (self.baseRegister.index | self.indexRegister.index << 3 | self.indexShift << 6) & 0xFF
        asm.write([sibVal])
        self.displacement.writeDataTo(asm)

    def __str__(self):
        return "[" + str(self.baseRegister) + " + " + str(self.indexRegister) + " << " + str(self.indexShift) + " + " + str(self.displacement) + "]"

    def __repr__(self):
        return "SIBMemoryOperand(%r, %r, %r, %r, %r)" % (self.baseRegister, self.indexRegister, self.indexShift, self.displacement, self.operandSize)