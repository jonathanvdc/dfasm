

class Instruction(object):
    """ Describes an instruction. """

    def __init__(self, name, operands):
        self.name = name
        self.operands = operands

    def __repr__(self):
        return "Instruction(" + str(self.name) + ", " + str(self.operands) + ")"
