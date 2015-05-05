
class TokenStream(object):
    """ Defines a token stream. """ 
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.skipTrivia()

    def peek(self):
        return self.tokens[self.index]

    def nextToken(self):
        self.index += 1
        if self.index >= len(self.tokens):
            raise StopIteration

    def skipTrivia(self):
        while self.peek().isTrivia():
            self.nextToken()

    def nextNoTrivia(self):
        self.nextToken()
        self.skipTrivia()

def parseToken(tokens):
    name = tokens[0]