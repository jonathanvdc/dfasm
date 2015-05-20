using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public class Section
    {
        public Section(
            string name,
            uint virtualSize,
            uint virtualAddress,
            IReadOnlyList<byte> rawData,
            IReadOnlyList<Relocation> relocations,
            IReadOnlyList<object> linenumbers,
            SectionHeaderFlags characteristics)
        {
            this.Name = name;
            this.VirtualSize = virtualSize;
            this.VirtualAddress = virtualAddress;
            this.RawData = rawData;
            this.Relocations = relocations;
            this.LineNumbers = linenumbers;
            this.Characteristics = characteristics;
        }

        public string Name { get; private set; }
        public uint VirtualSize { get; private set; }
        public uint VirtualAddress { get; private set; }
        public IReadOnlyList<byte> RawData { get; private set; }
        public IReadOnlyList<Relocation> Relocations { get; private set; }
        public IReadOnlyList<object> LineNumbers { get; private set; }
        public SectionHeaderFlags Characteristics { get; private set; }

        public IEnumerable<Relocation> GetRelocations(uint symbolIndex)
        {
            for (var i = 0; i < Relocations.Count; i++)
            {
                if (Relocations[i].SymbolIndex == symbolIndex)
                    yield return Relocations[i];
            }
        }
    }
}
