using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public enum SymbolComplexType : byte
    {
        Null,
        Pointer,
        Function,
        Array
    }
}
