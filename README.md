# dfasm
dfasm is an assembler that uses regular expressions to lex instructions.
It features an interactive REPL prompt, a COFF back-end, and a JIT engine (which is Windows only).

## Requirements
The following tools are required for dfasm to be run.

 * [IronPython 2.7](http://ironpython.net/)
 * A .Net Framework 4.5 implementation
   * .Net Framework 4.5 on Windows (present by default on recent versions of Windows)
   * [Mono](http://www.mono-project.com/download/#download-lin) on Linux or Mac OS X
 
## Invoking dfasm
You can open an interactive dfasm REPL prompt from the command line with:

    ipy dfasm.py

dfasm also takes several command line arguments:

    -d              Enable debugging output.
    -repl -r        Enable REPL mode (the default).
    -jit -j         Enable JIT mode.
    -coff           Output a COFF object file.
    -com            Output an MS-DOS COM file (experimental).

Options specific to the `-coff` or `-com` modes:

    -o:<file>       Set the output filename (the default is "a.o" or "a.com").
    
Options specific to the JIT engine:

    -arg:<value>    An argument to pass to the JIT'ed function.
    -ret:<type>     The return type to expect from the JIT'ed function.

## Optional tools
The following tools are not required, as they compile C# and D# source code for the .Net framework, which are included as libraries (`*.dll`) in the `src/dfasm/dfasm` folder. Thus, their usage is optional (but required when compiling said libraries yourself).

 * A C# 4.5 compiler
   * csc or [Roslyn](https://github.com/dotnet/roslyn) on Windows
   * [mcs](http://www.mono-project.com/docs/about-mono/languages/csharp/) on Mono
 * A somewhat recent D# compiler
   * [dsc](https://github.com/jonathanvdc/Flame/releases)
