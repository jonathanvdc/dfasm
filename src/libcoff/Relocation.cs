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
        public Relocation(BinaryReader reader)
        {
            this = default(Relocation);
            VirtualAddress = reader.ReadUInt32();
            SymbolIndex = reader.ReadUInt32();
            Type = (RelocationType)reader.ReadUInt16();
        }

        public Relocation(
            uint virtualAddress,
            uint symbolIndex,
            RelocationType type)
        {
            this = default(Relocation);
            this.VirtualAddress = virtualAddress;
            this.SymbolIndex = symbolIndex;
            this.Type = type;
        }

        public uint SymbolIndex { get; private set; }
        public uint VirtualAddress { get; private set; }
        public RelocationType Type { get; private set; }

        public void WriteTo(BinaryWriter writer)
        {
            writer.Write(VirtualAddress);
            writer.Write(SymbolIndex);
            writer.Write((ushort)Type);
        }
    }
}
