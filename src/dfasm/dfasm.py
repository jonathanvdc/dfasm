import clr
clr.AddReference("Automata.dll")
import sys

import Automata
import Instructions
import Assembler
from Lexer import *
from Parser import *

print("Ready.")

asm = Assembler.Assembler()

while not sys.stdin.closed:
    lexed = lexAsm(sys.stdin.readline().strip())
    print(lexed)
    instrs = parseAllInstructions(TokenStream(lexed))
    print(instrs)
    print(repr(instrs))

    for item in instrs:
        asm.process(item)
    
    for item in filter(lambda x: isinstance(x, InstructionNode), instrs):
        print("Operands:")
        print(repr(item.argumentList.toOperands(asm)))
    