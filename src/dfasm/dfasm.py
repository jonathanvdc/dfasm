import clr
clr.AddReference("Automata.dll")
clr.AddReference("libjit.dll")
import sys

import Automata
import Instructions
import Assembler
import libjit
import System
from Lexer import *
from Parser import *

print("Ready.")

debug = False
jit = True
repl = False

def printDebug(value):
    if debug:
        print(value)

def printHex(values):
    print("{ " + ", ".join(map(hex, values)) + " }")

asm = Assembler.Assembler()

previousIndex = 0

while not sys.stdin.closed:
    try:
        line = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        break
    lexed = lexAsm(line)
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
    
if jit:
    func = libjit.JitFunction.Create(System.Array[System.Byte](asm.code))
    print(func.Invoke[int]())
    func.Dispose()
elif repl:
    printHex(asm.code)