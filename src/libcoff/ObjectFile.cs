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
            var align = Is64Bit ? SectionHeaderFlags.Align16Bytes : SectionHeaderFlags.Align4Bytes;
            var arch = Is64Bit ? MachineType.Amd64 : MachineType.I386;

            var codeSection = new Section(".text", (uint)Code.Length, 0, Code, new Relocation[] { }, new object[] { }, SectionHeaderFlags.MemExecute | SectionHeaderFlags.MemRead | SectionHeaderFlags.CntCode | align);
            var dataSection = new Section(".data", 0, 0, new byte[] { }, new Relocation[] { }, new object[] { }, SectionHeaderFlags.MemRead | SectionHeaderFlags.MemWrite | SectionHeaderFlags.CntInitializedData | align);
            var bssSection = new Section(".bss", 0, 0, new byte[] { }, new Relocation[] { }, new object[] { }, SectionHeaderFlags.MemRead | SectionHeaderFlags.MemWrite | SectionHeaderFlags.CntUninitializedData | align);

            var sections = new Section[] { codeSection, dataSection, bssSection };

            var symbols = new List<Symbol>();

            symbols.Add(new Symbol(".file", SymbolMode.Debug, 0, codeSection, new SymbolType(), StorageClass.File, new IAuxiliarySymbol[] { new AuxiliaryFileName("fake") }));
            for (int i = 0; i < sections.Length; i++)
			{
                var item = sections[i];
			    symbols.Add(new Symbol(item.Name, SymbolMode.Normal, 0, item, new SymbolType(), StorageClass.Static, new IAuxiliarySymbol[] { new AuxiliarySectionDefinition(item, (ushort)(i + 1)) }));
			}

            symbols.Add(new Symbol("func", SymbolMode.Normal, 0, codeSection, new SymbolType(), StorageClass.External, new IAuxiliarySymbol[] { }));
            
            return new ObjectFile(arch, sections, symbols, 0);
        }
    }
}
