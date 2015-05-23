using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public struct Relocation
    {
        public Relocation(
            uint virtualAddress,
            Symbol Symbol,
            RelocationType type)
        {
            this = default(Relocation);
            this.VirtualAddress = virtualAddress;
            this.Symbol = Symbol;
            this.Type = type;
        }

        public Symbol Symbol { get; private set; }
        public uint VirtualAddress { get; private set; }
        public RelocationType Type { get; private set; }
    }
}
