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
        return self.size > 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Register(%r, %r, %r, %r)" % (self.name, self.index, self.size, self.isSegmentRegister)

registers = {
    "eax" : Register("eax", 0, 4, False),
    "ecx" : Register("ecx", 1, 4, False),
    "edx" : Register("edx", 2, 4, False),
    "ebx" : Register("ebx", 3, 4, False),
    "esp" : Register("esp", 4, 4, False), # Note: addressing memory based on esp is not allowed.
    "ebp" : Register("ebp", 5, 4, False),
    "esi" : Register("esi", 6, 4, False),
    "edi" : Register("edi", 7, 4, False),

    "al"  : Register("al", 0, 1, False),
    "cl"  : Register("cl", 1, 1, False),
    "dl"  : Register("dl", 2, 1, False),
    "bl"  : Register("bl", 3, 1, False),
    "ah"  : Register("al", 4, 1, False),
    "ch"  : Register("cl", 5, 1, False),
    "dh"  : Register("dl", 6, 1, False),
    "bh"  : Register("bl", 7, 1, False),

    "ax"  : Register("ax", 0, 2, False),
    "cx"  : Register("cx", 1, 2, False),
    "dx"  : Register("dx", 2, 2, False),
    "bx"  : Register("bx", 3, 2, False),
    "sp"  : Register("sp", 4, 2, False),
    "bp"  : Register("bp", 5, 2, False),
    "si"  : Register("si", 6, 2, False),
    "di"  : Register("di", 7, 2, False),
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
        """ Gets the operand value's size, in bytes. """
        return register.size

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

class EmptyDisplacementOperand(object):
    """ Represents an empty displacement operand. """
    def __init__(self):
        pass

    @property
    def operandSize(self):
        """ Gets the operand value's size, in bytes. """
        return 0

    def cast(self, size):
        """ "Casts" this operand to match the given size. """
        return ImmediateOperand(0, size)

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        pass

    def __str__(self):
        return "0"

    def __repr__(self):
        return "EmptyDisplacementOperand()"

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
        if -128 <= value <= 127:
            return ImmediateOperand(value, size8)
        elif -2 ** 15 <= value <= 2 ** 15 - 1:
            return ImmediateOperand(value, size16)
        else:
            return ImmediateOperand(value, size32)

    @staticmethod
    def createUnsigned(value):
        if 0 <= value <= 255:
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
        return MemoryOperand(self.value, self.addressRegister, self.displacement, size)

    @property
    def addressingMode(self):
        """ Gets the register operand's addressing mode. """
        if self.displacement.size == 1 or (self.addressRegister.index == 5 and self.displacement.size == 0):
            return "memoryByteOffset" # [register + disp8]
            # Note: [ebp] does not exist (its slot is taken by [disp32]. [ebp + disp8] does.
        elif self.displacement.size == 0:
            return "memory" # [register]
        else:
            return "memoryWordOffset" # [register + disp32]

    @property
    def operandIndex(self):
        """ Gets the register operand's 3-bit operand index. """
        return self.addressRegister.operandIndex

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        if self.addressRegister.index == 5 and self.displacement.size == 0:
            asm.write(0x00)
        else:
            self.displacement.writeDataTo(asm)

    def __str__(self):
        if self.displacement.size == 0:
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
        return MemoryOperand(self.value, self.baseRegister, self.indexRegister, self.indexShift, self.displacement, size)

    @property
    def addressingMode(self):
        """ Gets the register operand's addressing mode. """
        if self.offsetRegister.size == 0: 
            return "memory" # no displacement
        elif self.displacement.size == 1: 
            return "memoryByteOffset" # byte displacement
        else: 
            return "memoryWordOffset" # int displacement

    @property
    def operandIndex(self):
        """ Gets the register operand's 3-bit operand index. """
        return 4 # SIB uses operand index 4

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        sibVal = (self.baseRegister.Index | self.indexRegister.Index << 3 | self.indexShift << 6) & 0xFF;
        asm.write(sibVal);
        self.displacement.writeDataTo(asm);

    def __str__(self):
        return "[" + str(self.baseRegister) + " + " + str(self.indexRegister) + " << " + str(self.indexShift) + " + " + str(self.displacement) + "]"

    def __repr__(self):
        return "SIBMemoryOperand(%r, %r, %r, %r, %r)" % (self.baseRegister, self.indexRegister, self.indexShift, self.displacement, self.operandSize)