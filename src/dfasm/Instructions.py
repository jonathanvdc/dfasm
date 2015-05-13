import Assembler

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

class EmptyDisplacementOperand(object):
    """ Represents an empty displacement operand. """
    def __init__(self):
        pass

    @property
    def operandSize(self):
        """ Gets the operand value's size, in bytes. """
        return 0

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        pass

    def __str__(self):
        return "0"

    def __repr__(self):
        return "EmptyDisplacementOperand()"

class ImmediateOperand(object):
    """ Represents an immediate operand. """
    def __init__(self, value, encoding, operandSize):
        self.value = value
        self.encoding = encoding
        self.operandSize = operandSize

    def writeDataTo(self, asm):
        """ Writes operand data not in the opcode itself to the assembler. """
        asm.write(self.encoding(self.value))

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "ImmediateOperand(%r, %r, %r)" % (self.value, self.encoding, self.operandSize)

class MemoryOperand(object):
    """ Represents a simple memory operand. """
    def __init__(self, addressRegister, displacement, operandSize):
        self.addressRegister = addressRegister
        self.displacement = displacement
        self.operandSize = operandSize

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