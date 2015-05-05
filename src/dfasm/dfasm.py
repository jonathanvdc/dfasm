import clr
clr.AddReference("Automata.dll")
import sys

import Automata
import Instruction
from Lexer import *

while not sys.stdin.closed:
    lexed = lexAsm(sys.stdin.readline().strip())
    print(lexed)