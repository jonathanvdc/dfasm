
class TokenStream(object):
    """ Defines a token stream. """ 
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        pass

def parseToken(tokens):
    name = tokens[0]