import Automata

class Token:
    def __init__(self, contents, type):
        self.contents = contents
        self.type = type

    def isTrivia(self):
        # TODO: how do we mark comments as trivia?
        return self.type == 'whitespace'

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

def getAsmRegexes():
    return  { 
        "(_+c)(_+c+n)*"     : "identifier",
        "n*"                : "integer",
        "( +\n+\r+\t)*"     : "whitespace",
        "\\("               : "lparen",
        "\\)"               : "rparen",
        "["                 : "lbracket",
        "]"                 : "rbracket",
        ","                 : "comma",
        "\\+"               : "plus",
        "-"                 : "minus",
        "\\*"               : "asterisk",
        "."                 : "dot",
        ":"                 : "colon",
        ";"                 : "comment",
    }

def compileRegexes(regexDict):
    results = { }
    for k in regexDict.keys():
        regex = Automata.Interop.CompileRegex(k)
        results[regex.Optimize()] = regexDict[k]
        regex.Dispose() # Deallocate the old regex and use the optimized one instead
    return results

__defaultRegexes = None
def compileAsmRegexes():
    global __defaultRegexes
    if __defaultRegexes is None:
        __defaultRegexes = compileRegexes(getAsmRegexes())
    return __defaultRegexes

def getBestMatch(text, startIndex, regexes):
    result = "undefined"
    longest = -1
    for k in regexes.keys():
        match = longestSubstring(text, startIndex, k)
        if match > longest:
            result = regexes[k]
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

lexAsm = lambda text: lex(text, compileAsmRegexes())