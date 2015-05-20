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

        public static ObjectFile FromCode(byte[] Code)
        {
            var symbols = new Symbol[] { };
            var codeSection = new Section("code", (uint)Code.Length, 0, Code, new Relocation[] { }, new object[] { }, SectionHeaderFlags.MemExecute | SectionHeaderFlags.MemRead | SectionHeaderFlags.CntCode);
            var sections = new Section[] { codeSection };
            return new ObjectFile(MachineType.I386, sections, symbols, 0);
        }
    }
}
