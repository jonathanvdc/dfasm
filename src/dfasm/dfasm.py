import clr
clr.AddReference("Automata.dll")
import sys

import Automata
import Instructions
import Assembler
from Lexer import *
from Parser import *

print("Ready.")
while not sys.stdin.closed:
    lexed = lexAsm(sys.stdin.readline().strip())
    print(lexed)
    instr = parseInstruction(TokenStream(lexed))
    print(instr)
    print(repr(instr))
    print("Operands:")
    asm = Assembler.Assembler()
    print(repr(instr.argumentList.toOperands(asm)))