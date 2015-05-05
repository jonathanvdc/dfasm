import clr
clr.AddReference("Automata.dll")
import Automata

handle = Automata.Interop.CompileRegex("a+b*")
print(handle.GetInitialState().AddInput("aa").Accepts())
handle.Dispose()