import clr
clr.AddReference("Automata.dll")
import sys

import Automata
import Instruction

def longestSubstring(text, regex):
    state = regex.GetInitialState()
    i = 0
    length = -1
    while i < len(text):
        state = state.AddInput(text[i])
        if state.Accepts():
            length = i
        i += 1
    return length

def processChar(text):
    if text.isalpha():
        return 'c'
    elif text.isdigit():
        return 'n'
    else:
        return text

def processText(text):
    return map(processChar, text)
    

#lines = sys.stdin.readlines()

#for item in lines:
#    instr = parseInstruction(item)
#    print(instr)

# 'a', 'b' --> 'c'
# '0', '1' --> 'n'
# '#'      --> id('#')

# c*

regex = Automata.Interop.CompileRegex("c*")
print(len(regex.GetStates()))
print(longestSubstring(processText("mov eax ebx"), regex))
regex.Dispose()