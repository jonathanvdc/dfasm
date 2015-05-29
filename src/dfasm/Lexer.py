import Automata
import libdiagnostics
from libdiagnostics import DiagnosticsException

class Token(object):
    """ A token of a certain type, at the given location in the file. """
    def __init__(self, contents, type, location):
        """ `contents` is the string represented by this token, and `type` is
        its type as a string; a key in `asmRegexes`. `location` is a
        SourceLocation object specifying the location of the token in the
        source code. """
        self.contents = contents
        self.type = type
        self.location = location

    def isTrivia(self):
        return self.type in ('whitespace', 'comment', 'newline')

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

# A dictionary containing the regex for each type of token. Before strings are
# compared to these regexes, alphabet characters [a-zA-Z] are turned into 'c's
# and digits [0-9] are turned into 'n's (by processText): this significantly
# simplifies the expressions, and speeds up matching on them.

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

def makeDFA(regex):
    """ Compile the given regex to a deterministic finite-state automaton. """
    compiled = Automata.Interop.Instance.CompileRegex(regex)
    dfa = compiled.Optimize()
    return dfa

compiledRegexes = {type: makeDFA(regex) for type, regex in asmRegexes.items()}

def getBestMatch(text, startIndex, grammar):
    result = "undefined"
    longest = -1
    for type, dfa in grammar.items():
        match = longestSubstring(text, startIndex, dfa)
        if match > longest:
            result = type
            longest = match

    if longest <= 0:
        # If we can't match at all, return a single-char "unrecognized" token.
        return "undefined", startIndex + 1

    return result, longest

def lex(doc, grammar):
    """ Lex the given SourceDocument into tokens, using a dictionary that maps
    maps token types (strings) to DFA objects. """
    results = []
    size = 0
    text = doc.Source
    processedText = processText(text)
    while size < len(processedText):
        type, newSize = getBestMatch(processedText, size, grammar)
        location = libdiagnostics.SourceLocation(doc, size, newSize - size)
        token = Token(text[size:newSize], type, location)
        results.append(token)
        size = newSize
    return results

def joinTokens(tokens, type):
    contents = "".join(t.contents for t in tokens)
    location = tokens[0].location
    for t in tokens[1:]:
        location = location.Between(t.location)

    return Token(contents, type, location)

def processComments(tokens):
    result = []
    i = 0
    while i < len(tokens):
        if tokens[i].type == "semicolon":
            commentTokens = []
            while i < len(tokens) and tokens[i].type != "newline":
                commentTokens.append(tokens[i])
                i += 1
            result.append(joinTokens(commentTokens, "comment"))
        else:
            result.append(tokens[i])
            i += 1
    return result

def processStrings(tokens):
    result = []
    currentString = None
    startLocation = None

    for t in tokens:
        if t.type == "quote":
            if currentString is None:
                # Open a new string, and begin collecting tokens into it.
                currentString = []
                startLocation = t.location
            else:
                # Close the string and push its ASCII values as comma-
                # separated tokens: for example, `"abc"` will parse into the
                # same list of tokens as `97,98,99`.
                loc = startLocation.Between(t.location)
                fullString = ''.join(currentString).decode('string_escape')
                for i, c in enumerate(fullString):
                    if i > 0:
                        result.append(Token(',', 'comma', loc))
                    result.append(Token(str(ord(c)), 'integer', loc))
                currentString = None
        elif currentString is not None:
            currentString.append(t.contents)
        else:
            result.append(t)

    if currentString is not None:
        raise DiagnosticsException("Mismatched quotes",
                                   "While scanning a string literal, a closing quote was not found.", startLocation)

    return result

process = lambda tokens: processComments(processStrings(tokens))

lexAsm = lambda text: process(lex(text, compiledRegexes))

