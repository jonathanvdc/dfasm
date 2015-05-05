import Automata

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
        " +\n+\r+\t"        : "whitespace"
    }

def compileRegexes(regexDict):
    results = { }
    for k in regexDict.keys():
        results[Automata.Interop.CompileRegex(k)] = regexDict[k]
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

    if longest == -1:
        return result, startIndex # Be generous and return a single-character string

    return result, longest

def lex(text, regexes):
    results = []
    size = 0
    processedText = processText(text)
    while size < len(processedText):
        type, newSize = getBestMatch(processedText, size, regexes)
        results.append((text[size:newSize], type))
        size = newSize
    return results

lexAsm = lambda text: lex(text, compileAsmRegexes())