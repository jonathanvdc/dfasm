import clr
clr.AddReference("Automata.dll")
import sys

import Automata
import Instruction
from Lexer import *
    
#lines = sys.stdin.readlines()

#for item in lines:
#    instr = parseInstruction(item)
#    print(instr)

# 'a', 'b' --> 'c'
# '0', '1' --> 'n'
# '#'      --> id('#')

# c*

print(lexAsm("mov eax [ebx*4+3]"))
regex.Dispose()