import clr
clr.AddReference("Automata.dll")
import sys

import Automata
import Instruction
from Lexer import *
from Parser import *

print("Ready.")
while not sys.stdin.closed:
    lexed = lexAsm(sys.stdin.readline().strip())
    print(lexed)
    instr = parseInstruction(TokenStream(lexed))
    print(instr)
    print(repr(instr))