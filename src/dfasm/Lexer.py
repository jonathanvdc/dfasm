import Automata

class Token(object):
    def __init__(self, contents, type):
        self.contents = contents
        self.type = type

    def isTrivia(self):
        return self.type == 'whitespace' or self.type == 'comment' or self.type == 'newline'

    def __str__(self):
        return self.contents

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
    "whitespace": "( +\r+\t)*",
    "newline" : "\n*",
    "lparen": "\\(",
    "rparen": "\\)",
    "lbracket": "[",
    "rbracket": "]",
    "comma": ",",
    "plus": "\\+",
    "minus": "-",
    "asterisk": "\\*",
    "slash" : "/",
    "percent": "%",
    "or" : "|",
    "and" : "&",
    "greaterthangreaterthan" : ">>",
    "lessthanlessthan" : "<<",
    "dot": ".",
    "colon": ":",
    "semicolon": ";"
}

# Compile regexes to automata.
def makeDFA(regex):
    compiled = Automata.Interop.Instance.CompileRegex(regex)
    dfa = compiled.Optimize()
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

def combineTokens(tokens, type):
    return Token("".join(map(lambda x: x.contents, tokens)), type)

def processComments(tokens):
    results = []
    i = 0
    while i < len(tokens):
        if tokens[i].type == "semicolon":
            commentTokens = []
            while i < len(tokens) and tokens[i].type != "newline":
                commentTokens.append(tokens[i])
                i += 1
            results.append(combineTokens(commentTokens, "comment"))
        else:
            results.append(tokens[i])
            i += 1
    return results

lexAsm = lambda text: processComments(lex(text, asmRegexes))
