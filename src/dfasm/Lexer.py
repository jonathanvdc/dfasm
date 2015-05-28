import Automata
import libdiagnostics

class Token(object):
    def __init__(self, contents, type, location):
        self.contents = contents
        self.type = type
        self.location = location

    def isTrivia(self):
        return self.type == 'whitespace' or self.type == 'comment' or self.type == 'newline'

    def __str__(self):
        return self.contents

    def __repr__(self):
        return 'Token(%r, %r, %r)' % (self.contents, self.type, self.location)

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
    "integer"   : "n*",
    "whitespace": "( +\r+\t)*",
    "newline"   : "\n*",
    "lparen"    : "\\(",
    "rparen"    : "\\)",
    "lbracket"  : "[",
    "rbracket"  : "]",
    "comma"     : ",",
    "plus"      : "\\+",
    "minus"     : "-",
    "asterisk"  : "\\*",
    "slash"     : "/",
    "percent"   : "%",
    "ampersand" : "&",
    "bar"       : "|",
    "rshift"    : ">>",
    "lshift"    : "<<",
    "dot"       : ".",
    "colon"     : ":",
    "semicolon" : ";",
    "quote"     : '"',
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

def lex(doc, regexes):
    results = []
    size = 0
    text = doc.Source
    processedText = processText(text)
    while size < len(processedText):
        type, newSize = getBestMatch(processedText, size, regexes)
        token = Token(text[size:newSize], type, libdiagnostics.SourceLocation(doc, size, newSize - size))
        results.append(token)
        size = newSize
    return results

def combineTokens(tokens, type, loc):
    return Token("".join(map(lambda x: x.contents, tokens)), type, loc)

def processComments(tokens):
    results = []
    i = 0
    while i < len(tokens):
        if tokens[i].type == "semicolon":
            commentTokens = []
            while i < len(tokens) and tokens[i].type != "newline":
                commentTokens.append(tokens[i])
                i += 1
            results.append(combineTokens(commentTokens, "comment", commentTokens[0].location))
        else:
            results.append(tokens[i])
            i += 1
    return results

def processStrings(tokens):
    result = []
    currentString = None
    for t in tokens:
        if t.type == "quote":
            if currentString is None:
                # Open a new string, and begin collecting tokens into it.
                currentString = []
            else:
                # Close the string and push its ASCII values as comma-
                # separated tokens: for example, `"abc"` will parse into the
                # same list of tokens as `97,98,99`.
                fullString = ''.join(currentString).decode('string_escape')
                for i, c in enumerate(fullString):
                    if i > 0:
                        result.append(Token(',', 'comma', t.location))
                    result.append(Token(str(ord(c)), 'integer', t.location))
                currentString = None
        elif currentString is not None:
            currentString.append(t.contents)
        else:
            result.append(t)

    return result

process = lambda tokens: processComments(processStrings(tokens))

lexAsm = lambda text: process(lex(text, asmRegexes))

