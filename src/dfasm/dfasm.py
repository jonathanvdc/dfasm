import clr
clr.AddReference("Automata.dll")
clr.AddReference("libjit.dll")
clr.AddReference("libcoff.dll")
import sys

import Automata
import Instructions
import Assembler
import libjit
import System
import libcoff
from Lexer import *
from Parser import *

print("Ready.")

debug = False
jit = False
repl = False
output = True

def printDebug(value):
    if debug:
        print(value)

def printHex(values):
    text = "{ " + ", ".join(map(lambda x: hex(x) if isinstance(x, int) else str(x), values)) + " }"
    print(text)

asm = Assembler.Assembler()

previousIndex = 0

while not sys.stdin.closed:
    try:
        line = ""
        while line == "" and not sys.stdin.closed:
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
        previousIndex = len(asm.code)
    
asm.patchLabels()
print("")
if jit:
    func = libjit.JitFunction.Create(System.Array[System.Byte](asm.code))
    print(func.Invoke[int]())
    func.Dispose()
elif repl:
    printHex(asm.code)
elif output:
    coffFile = libcoff.ObjectFile.FromCode(System.Array[System.Byte](asm.code), True)
    libcoff.CoffWriter.WriteToFile("a.o", coffFile)