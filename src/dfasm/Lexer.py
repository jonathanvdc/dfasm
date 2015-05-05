import Automata

class Token:
    def __init__(self, contents, type):
        self.contents = contents
        self.type = type

    def isTrivia(self):
        # TODO: how do we mark comments as trivia?
        return self.type == 'whitespace'

    def __repr__(self):
        return 'Token(%r, %r)' % (self.contents, self.type)

def longestSubstring(text, startIndex, regex):
    state = regex.GetInitialState()
    i = startIndex
    endIndex = -1
    while i < len(text):
        state = state.AddInput(text[i])
        if state.Accepts():
            endIndex = i
        i += 1
    return endIndex + 1

def processChar(text):
    if text.isalpha():
        return 'c'
    elif text.isdigit():
        return 'n'
    else:
        return text

def processText(text):
    return map(processChar, text)

asmRegexes = {
    "identifier": "(_+c)(_+c+n)*",
    "integer": "n*",
    "whitespace": "( +\n+\r+\t)*",
    "lparen": "\\(",
    "rparen": "\\)",
    "lbracket": "[",
    "rbracket": "]",
    "comma": ",",
    "plus": "\\+",
    "minus": "-",
    "asterisk": "\\*",
    "dot": ".",
    "colon": ":",
    "semicolon": ";",
}

# Compile regexes to automata.
def makeDFA(regex):
    compiled = Automata.Interop.CompileRegex(regex)
    dfa = compiled.Optimize()
    compiled.Dispose()
    return dfa

asmRegexes = {type: makeDFA(regex) for type, regex in asmRegexes.items()}

def getBestMatch(text, startIndex, grammar):
    result = "undefined"
    longest = -1
    for type, dfa in grammar.items():
        match = longestSubstring(text, startIndex, dfa)
        if match > longest:
            result = type
            longest = match

    if longest <= 0:
        return "undefined", startIndex + 1 # Be generous and return a single-character string

    return result, longest

def lex(text, regexes):
    results = []
    size = 0
    processedText = processText(text)
    while size < len(processedText):
        type, newSize = getBestMatch(processedText, size, regexes)
        token = Token(text[size:newSize], type)
        results.append(token)
        size = newSize
    return results

lexAsm = lambda text: lex(text, asmRegexes)
