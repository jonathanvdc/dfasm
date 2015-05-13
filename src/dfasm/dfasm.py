import clr
clr.AddReference("Automata.dll")
import sys

import Automata
import Instructions
import Assembler
from Lexer import *
from Parser import *

print("Ready.")

debug = False
repl = True

def printDebug(value):
    if debug:
        print(value)

def printHex(values):
    print("{ " + ", ".join(map(hex, values)) + " }")

asm = Assembler.Assembler()

previousIndex = 0

while not sys.stdin.closed:
    lexed = lexAsm(sys.stdin.readline().strip())
    printDebug(lexed)
    instrs = parseAllInstructions(TokenStream(lexed))
    printDebug(instrs)
    printDebug(repr(instrs))

    for item in instrs:
        asm.process(item)
    
    if debug:
        for item in filter(lambda x: isinstance(x, InstructionNode), instrs):
            print("Operands:")
            print(repr(item.argumentList.toOperands(asm)))

    if repl:
        printHex(asm.code[previousIndex:])
        previousIndex = asm.index
    
if not repl:
    printHex(asm.code)