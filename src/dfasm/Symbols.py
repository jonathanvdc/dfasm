from Encoding import *

class LocalSymbol(object):
    """ Represents a locally defined symbol. """
    def __init__(self, name, offset = None, isPublic = False):
        self.name = name
        self.offset = offset
        self.isPublic = isPublic

    def __str__(self):
        return str(self.name) if not self.isPublic else ".global " + str(self.name)

    def __repr__(self):
        return "StaticSymbol(%r, %r, %r, %r)" % (self.name, self.offset, self.isPublic)

    def makePublic(self):
        """ Makes this local symbol public. """
        self.isPublic = True

    def define(self, other):
        """ Defines this local symbol's name and offset. """
        if isinstance(other, ExternalSymbol):
            raise Exception("'" + str(self) + "' cannot be made external because symbols must be either external, global or local.")

        self.name = other.name
        if not self.isDefined:
            if other.isDefined:
                self.offset = other.offset
        elif other.isDefined:
            raise Exception("Symbol '" + str(self) + "' is defined more than once.")
        if other.isPublic:
            self.makePublic()

    @property
    def isDefined(self):
        """ Gets a boolean value that indicates whether the local symbol has been defined. """
        return self.offset is not None

    @property
    def isExternal(self):
        return False

class ExternalSymbol(object):
    """ Represents an externally defined symbol. """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return ".extern " + str(self.name)

    def __repr__(self):
        return "ExternalSymbol(%r)" % (self.name)

    @property
    def offset(self):
        """ Gets the external symbol's "offset". This is a dummy value. """
        return 0

    @property
    def isExternal(self):
        return True

    @property
    def isDefined(self):
        """ Gets a boolean value that indicates whether the external symbol has been defined. """
        return True

    def makePublic(self):
        """ Makes this external symbol public (global). """
        raise Exception("'" + str(self) + "' cannot be made global because symbols cannot be both external and global.")

    def define(self, other):
        """ "Defines" this external symbol. """
        raise Exception("'" + str(self) + "' cannot be defined locally because it is external. Did you mean to declare '" + 
                        str(self.name) + "' as '.global " + str(self.name) + "' instead?")