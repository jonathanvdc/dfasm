import functools

def to8(x):
    """ Convert a given integer to a single-byte list. """
    return [x & 0xFF]

def to16le(x):
    """ Convert a given integer to its 16-bit little endian representation as
    a list of two bytes. """
    return [(x >>  0) & 0xFF,
            (x >>  8) & 0xFF]

def to32le(x):
    """ Convert a given integer to its 32-bit little endian representation as
    a list of four bytes. """
    return [(x >>  0) & 0xFF,
            (x >>  8) & 0xFF,
            (x >> 16) & 0xFF,
            (x >> 24) & 0xFF]

def relative(enc, here):
    """ Given an address encoding function and an offset, return a new
    function that encodes addresses relative to the given offset."""
    return lambda x: enc(x - here)

@functools.total_ordering
class OperandSize(object):
    """ Represents an operand's size. """
    def __init__(self, size, encoding):
        self.size = size
        self.encoding = encoding

    def __str__(self):
        return str(self.size)

    def __repr__(self):
        return "OperandSize(%r, %r)" % (self.size, self.encoding)

    def __gt__(self, other):
        return self.size > other.size

    def __eq__(self, other):
        return self.size == other.size

size0 = OperandSize(0, lambda x: []) # Represents zero, which can usually be omitted. If not, it will probably be upcast somehow. Meh.
size8 = OperandSize(1, to8)
size16 = OperandSize(2, to16le)
size32 = OperandSize(4, to32le)
