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

    public class Symbol
    {
        public Symbol(string name, uint value, Section section, StorageClass storageClass)
            : this(name, SymbolMode.Normal, value, section, storageClass)
        {
        }
        public Symbol(string name, SymbolMode mode, uint value, Section section, StorageClass storageClass)
        {
            this.Name = name;
            this.Value = value;
            this.Section = section;
            this.StorageClass = storageClass;
            this.Mode = mode;
            this.AuxiliarySymbols = new IAuxiliarySymbol[0];
        }
        public Symbol(
            string name,
            SymbolMode mode,
            uint value,
            Section section,
            SymbolType type,
            StorageClass storageClass,
            IReadOnlyList<IAuxiliarySymbol> auxiliarySymbols)
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
        public IReadOnlyList<IAuxiliarySymbol> AuxiliarySymbols { get; private set; }
    }
}
