using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public enum SymbolMode
    {
        Undefined,
        Normal,
        Absolute,
        Debug,
    }

    public struct AuxiliarySymbol
    {
        public AuxiliarySymbol(IReadOnlyList<byte> data)
        {
            this = default(AuxiliarySymbol);
            this.Data = data;
        }

        public IReadOnlyList<byte> Data { get; private set; }
    }

    public class Symbol
    {
        public Symbol(
            string name,
            SymbolMode mode,
            uint value,
            Section section,
            SymbolType type,
            StorageClass storageClass,
            IReadOnlyList<AuxiliarySymbol> auxiliarySymbols)
        {
            this.Name = name;
            this.Mode = mode;
            this.Value = value;
            this.Section = section;
            this.Type = type;
            this.StorageClass = storageClass;
            this.AuxiliarySymbols = auxiliarySymbols;
        }

        public const int Size = 18;
        
        public string Name { get; private set; }
        public SymbolMode Mode { get; private set; }
        public uint Value { get; private set; }
        public Section Section { get; private set; }
        public SymbolType Type { get; private set; }
        public StorageClass StorageClass { get; private set; }
        public IReadOnlyList<AuxiliarySymbol> AuxiliarySymbols { get; private set; }
    }
}
