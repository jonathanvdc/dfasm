using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public class ObjectFile
    {
        public ObjectFile(
            MachineType machine,
            IReadOnlyList<Section> sections,
            IReadOnlyList<Symbol> symbols,
            CoffHeaderFlags characteristics)
        {
            this.Machine = machine;
            this.Sections = sections;
            this.Symbols = symbols;
            this.Characteristics = characteristics;
        }

        public CoffHeaderFlags Characteristics { get; private set; }
        public IReadOnlyList<Symbol> Symbols { get; private set; }
        public IReadOnlyList<Section> Sections { get; private set; }
        public MachineType Machine { get; private set; }

        public int GetSectionIndex(Section Value)
        {
            for (int i = 0; i < Sections.Count; i++)
            {
                if (Sections[i] == Value)
                {
                    return i;
                }
            }
            return -1;
        }

        public static ObjectFile FromCode(byte[] Code, bool Is64Bit)
        {
            var dataSection = new Section(".data", 0, 0, new byte[] { }, new Relocation[] { }, new object[] { }, SectionHeaderFlags.MemRead | SectionHeaderFlags.MemWrite);
            var codeSection = new Section(".text", (uint)Code.Length, 0, Code, new Relocation[] { }, new object[] { }, SectionHeaderFlags.MemExecute | SectionHeaderFlags.MemRead | SectionHeaderFlags.CntCode | SectionHeaderFlags.Align16Bytes);
            var function = new Symbol("func", SymbolMode.Normal, 0, codeSection, new SymbolType(), StorageClass.External, new AuxiliarySymbol[] { });
            var sections = new Section[] { dataSection, codeSection };
            var symbols = new Symbol[] { function };
            return new ObjectFile(Is64Bit ? MachineType.Amd64 : MachineType.I386, sections, symbols, 0);
        }
    }
}
