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

debug = False
jit = False
repl = True
output = None

def printDebug(value):
    if debug:
        print(value)

def printHex(values):
    text = "{ " + ", ".join(map(lambda x: hex(x) if isinstance(x, int) else str(x), values)) + " }"
    print(text)

def getCoffStorageClass(symbol):
    if symbol.isExternal or symbol.isPublic:
        return libcoff.StorageClass.External
    else:
        return libcoff.StorageClass.Static

def getCoffRelocationType(is64Bit, reloc):
    if reloc.operandSize != size32:
        raise Exception("Non-32-bit relocations are not supported.")

    if reloc.isRelative: # I don't think we need to account for 16-bit relocations.
                         # We don't emit those, and doing so anyway would be dangerous.
        return libcoff.RelocationType.AMD64_REL32 if is64Bit else libcoff.RelocationType.I386_REL32
    else:
        return libcoff.RelocationType.AMD64_ADDR32 if is64Bit else libcoff.RelocationType.I386_DIR32

def createObjectFile(asm, is64Bit):
    align = libcoff.SectionHeaderFlags.Align16Bytes if is64Bit else SectionHeaderFlags.Align4Bytes
    arch = libcoff.MachineType.Amd64 if is64Bit else libcoff.MachineType.I386

    code = System.Array[System.Byte](asm.code)

    codeSection = libcoff.Section(".text", 0, libcoff.SectionHeaderFlags.MemExecute | libcoff.SectionHeaderFlags.MemRead | libcoff.SectionHeaderFlags.CntCode | align, code)    
    dataSection = libcoff.Section(".data", 0, libcoff.SectionHeaderFlags.MemRead | libcoff.SectionHeaderFlags.MemWrite | libcoff.SectionHeaderFlags.CntInitializedData | align)
    bssSection = libcoff.Section(".bss", 0, libcoff.SectionHeaderFlags.MemRead | libcoff.SectionHeaderFlags.MemWrite | libcoff.SectionHeaderFlags.CntUninitializedData | align)

    sections = System.Array[libcoff.Section]([codeSection, dataSection, bssSection])

    symbols = System.Collections.Generic.List[libcoff.Symbol]()

    symbols.Add(libcoff.Symbol(".file", libcoff.SymbolMode.Debug, 0, codeSection, libcoff.SymbolType(), libcoff.StorageClass.File, System.Array[libcoff.IAuxiliarySymbol]([libcoff.AuxiliaryFileName("fake")])))
    for i in range(len(sections)):
        item = sections[i]
        symbols.Add(libcoff.Symbol(item.Name, libcoff.SymbolMode.Normal, 0, item, libcoff.SymbolType(), libcoff.StorageClass.Static, System.Array[libcoff.IAuxiliarySymbol]([libcoff.AuxiliarySectionDefinition(item, i + 1)])))

    for sym in asm.symbols.values():
        newSymbol = libcoff.Symbol(sym.name, sym.offset, codeSection if not sym.isExternal else None, getCoffStorageClass(sym))
        symbols.Add(newSymbol)
        for reloc in asm.relocations:
            if reloc.symbol == sym:
                codeSection.Relocations.Add(libcoff.Relocation(reloc.offset, newSymbol, getCoffRelocationType(is64Bit, reloc)))
            
    return libcoff.ObjectFile(arch, sections, symbols, libcoff.CoffHeaderFlags())

asm = Assembler.Assembler()

previousIndex = 0

if sys.stdin.isatty():
    print("Ready.")
    while sys.stdin:
        try:
            line = ""
            while line == "" and sys.stdin:
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
else:
    for line in sys.stdin:
        lexed = lexAsm(line)
        instrs = parseAllInstructions(TokenStream(lexed))
        for item in instrs:
            asm.process(item)
    
if sys.stdin.isatty():
    print("")
if jit:
    virtBuf = libjit.VirtualBuffer.Create(asm.index)
    asm.baseOffset = virtBuf.Address
    asm.patchLabels()
    virtBuf.Write(System.Array[System.Byte](asm.code))
    func = libjit.JitFunction(virtBuf)
    print(func.Invoke[int]())
    func.Dispose()
elif repl:
    asm.patchLabels()
    printHex(asm.code)
elif output == "coff":
    asm.baseOffset = 0
    asm.relocateAbsolutes = False
    asm.patchLabels()
    coffFile = createObjectFile(asm, True)
    libcoff.CoffWriter.WriteToFile("a.o", coffFile)
elif output == "com":
    asm.baseOffset = 0x100
    asm.patchLabels()
    target = System.IO.FileStream("a.com", System.IO.FileMode.Create, System.IO.FileAccess.Write)
    target.Write(System.Array[System.Byte](asm.code), 0, len(asm.code))
    target.Dispose()