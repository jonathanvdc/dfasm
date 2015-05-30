import clr
clr.AddReference("Automata.dll")
clr.AddReference("libjit.dll")
clr.AddReference("libcoff.dll")
clr.AddReference("libdiagnostics.dll")
import sys

import System
import Automata
import Instructions
import Assembler
import libjit
import libcoff
import libdiagnostics
from Lexer import *
from Parser import *
from libdiagnostics import DiagnosticsException

def printDebug(value):
    if debug:
        print(value)

def printHex(values):
    def showValue(x):
        if isinstance(x, int):
            return '%02X' % x
        else:
            return str(x)
    print("{ %s }" % ", ".join(showValue(x) for x in values))

def getCoffStorageClass(symbol):
    if symbol.isExternal or symbol.isPublic:
        return libcoff.StorageClass.External
    else:
        return libcoff.StorageClass.Static

def getCoffRelocationType(is64Bit, reloc):
    if reloc.operandSize != size32:
        raise ValueError("Non-32-bit relocations are not supported.")

    if reloc.isRelative: # I don't think we need to account for 16-bit relocations.
                         # We don't emit those, and doing so anyway would be dangerous.
        return libcoff.RelocationType.AMD64_REL32 if is64Bit else libcoff.RelocationType.I386_REL32
    else:
        return libcoff.RelocationType.AMD64_ADDR32 if is64Bit else libcoff.RelocationType.I386_DIR32

def createObjectFile(asm, is64Bit):
    
    align = libcoff.SectionHeaderFlags.Align16Bytes if is64Bit else SectionHeaderFlags.Align4Bytes
    arch = libcoff.MachineType.Amd64 if is64Bit else libcoff.MachineType.I386

    # This section layout is copied from gcc, so it ought to work.
    code = System.Array[System.Byte](asm.code)

    codeSection = libcoff.Section(".text", 0, libcoff.SectionHeaderFlags.MemExecute
                                            | libcoff.SectionHeaderFlags.MemRead
                                            | libcoff.SectionHeaderFlags.CntCode
                                            | align, code)    
    dataSection = libcoff.Section(".data", 0, libcoff.SectionHeaderFlags.MemRead
                                            | libcoff.SectionHeaderFlags.MemWrite
                                            | libcoff.SectionHeaderFlags.CntInitializedData
                                            | align)
    bssSection = libcoff.Section(".bss", 0, libcoff.SectionHeaderFlags.MemRead
                                          | libcoff.SectionHeaderFlags.MemWrite
                                          | libcoff.SectionHeaderFlags.CntUninitializedData
                                          | align)

    sections = System.Array[libcoff.Section]([codeSection, dataSection, bssSection])

    # Collect all our used symbols to write them to the COFF file.
    symbols = System.Collections.Generic.List[libcoff.Symbol]()

    # Define a "fake" file directive: this is a gcc hack.
    auxSymbols = System.Array[libcoff.IAuxiliarySymbol]([libcoff.AuxiliaryFileName("fake")])
    symbols.Add(libcoff.Symbol(".file", libcoff.SymbolMode.Debug, 0, codeSection,
                               libcoff.SymbolType(), libcoff.StorageClass.File, auxSymbols))
    
    # Each section has its own entry in the symbol table.
    for i in range(len(sections)):
        section = sections[i]
        sectDef = libcoff.AuxiliarySectionDefinition(section, i + 1)
        auxSymbols = System.Array[libcoff.IAuxiliarySymbol]([sectDef])
        symbols.Add(libcoff.Symbol(section.Name, libcoff.SymbolMode.Normal, 0, section,
                                   libcoff.SymbolType(), libcoff.StorageClass.Static, auxSymbols))

    # Finally, actually put the symbols from our code in the table.
    for sym in asm.symbols.values():
        sec = None if sym.isExternal else codeSection
        newSymbol = libcoff.Symbol(sym.name, sym.offset, sec, getCoffStorageClass(sym))
        symbols.Add(newSymbol)
        for reloc in asm.relocations:
            # Append all of the relevant relocations.
            if reloc.symbol == sym:
                relocType = getCoffRelocationType(is64Bit, reloc)
                relocObject = libcoff.Relocation(reloc.offset, newSymbol, relocType)
                codeSection.Relocations.Add(relocObject)
            
    return libcoff.ObjectFile(arch, sections, symbols, libcoff.CoffHeaderFlags())

def getEntryPoint(asm):
	return asm.getSymbol("main") if (asm.hasSymbol("main") and asm.getSymbol("main").isPublic) else None
	
def getEntryPointOffset(asm):
    return getEntryPoint(asm).offset if getEntryPoint(asm) != None else 0

debug = False
jit = False
repl = True
output = None

for argument in sys.argv[1:]:
	if argument == "-d":
		debug = True
	elif argument == "-jit" or argument == "-j":
		jit = True
		repl = False
	elif argument == "-repl" or argument == "-r":
		jit = False
		repl = True
	elif argument == "-coff":
		jit = False
		repl = False
		output = "a.o"
	elif argument == "-com":
		jit = False
		repl = False
		output = "a.com"
	elif argument[0:3] == "-o:":
		jit = False
		repl = False
		output = argument[3:]

asm = Assembler.Assembler()

previousIndex = 0
lineIndex = 0

log = libdiagnostics.ConsoleLog(libdiagnostics.ConsoleEnvironment.AcquireConsole())

if sys.stdin.isatty():
    print("Ready.")
    while sys.stdin:
        try:
            line = ""
            while line == "" or line.isspace():
                line = sys.stdin.readline()
                lineIndex += 1
        except KeyboardInterrupt:
            break

        doc = libdiagnostics.SourceDocument(line, "line " + str(lineIndex))
        try:
            lexed = lexAsm(doc)
        except DiagnosticsException as ex:
            log.LogError(ex.Entry)
            continue
        printDebug(lexed)
        instrs = parseAllInstructions(TokenStream(lexed, doc, log))
        printDebug(instrs)
        printDebug(repr(instrs))

        for item in instrs:
            try:
                try:
                    asm.process(item)
                except ValueError as ex:
                    wholeLine = libdiagnostics.SourceLocation(doc, 0, len(line))
                    raise DiagnosticsException('Invalid', str(ex), wholeLine)
            except DiagnosticsException as ex:
                log.LogError(ex.Entry)
            
        if debug:
            for item in filter(lambda x: isinstance(x, InstructionNode), instrs):
                print("Operands:")
                print(repr(item.argumentList.toOperands(asm)))

        if repl:
            printHex(asm.code[previousIndex:])
            previousIndex = len(asm.code)
    print("")
else:
    for line in sys.stdin:
        lineIndex += 1
        doc = libdiagnostics.SourceDocument(line, "line " + str(lineIndex))
        try:
            lexed = lexAsm(doc)
        except libdiagnostics.DiagnosticsException as ex:
            log.LogError(ex.Entry)
            continue
        instrs = parseAllInstructions(TokenStream(lexed, doc, log))
        for item in instrs:
            try:
                asm.process(item)
            except libdiagnostics.DiagnosticsException as ex:
                log.LogError(ex.Entry)

if jit:
    virtBuf = libjit.VirtualBuffer.Create(asm.index)
    asm.baseOffset = int(virtBuf.Pointer)
    asm.patchLabels()
    virtBuf.Write(System.Array[System.Byte](asm.code))
    func = libjit.JitFunction(virtBuf, getEntryPointOffset(asm))
    print(func.Invoke[int]())
    func.Dispose()
elif repl:
    asm.patchLabels()
    printHex(asm.code)
elif output.endswith(".o"):
    asm.baseOffset = 0
    asm.relocateAbsolutes = False
    asm.patchLabels()
    coffFile = createObjectFile(asm, True)
    libcoff.CoffWriter.WriteToFile(output, coffFile)
elif output.endswith(".com"):
    asm.baseOffset = 0x100
    asm.patchLabels()
    entryPoint = getEntryPoint(asm)
    offset = getEntryPointOffset(asm)
    if offset != 0:
        # 0xe9 is a relative JMP instruction.
        asm.code[:0] = [0xe9] + to32le(offset)
    target = System.IO.FileStream(output, System.IO.FileMode.Create, System.IO.FileAccess.Write)
    target.Write(System.Array[System.Byte](asm.code), 0, len(asm.code))
    target.Dispose()