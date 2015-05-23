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
            uint virtualAddress,
            SectionHeaderFlags characteristics)
        {
            this.Name = name;
            this.VirtualAddress = virtualAddress;
            this.RawData = new List<byte>();
            this.Relocations = new List<Relocation>();
            this.LineNumbers = new List<object>();
            this.Characteristics = characteristics;
        }
        public Section(
            string name,
            uint virtualAddress,
            SectionHeaderFlags characteristics,
            IEnumerable<byte> rawData)
        {
            this.Name = name;
            this.VirtualAddress = virtualAddress;
            this.RawData = new List<byte>(rawData);
            this.Relocations = new List<Relocation>();
            this.LineNumbers = new List<object>();
            this.Characteristics = characteristics;
        }
        public Section(
            string name,
            uint virtualAddress,
            SectionHeaderFlags characteristics,
            IEnumerable<byte> rawData,
            IEnumerable<Relocation> relocations,
            IEnumerable<object> linenumbers)
        {
            this.Name = name;
            this.VirtualAddress = virtualAddress;
            this.RawData = new List<byte>(rawData);
            this.Relocations = new List<Relocation>(relocations);
            this.LineNumbers = new List<object>(linenumbers);
            this.Characteristics = characteristics;
        }

        public string Name { get; private set; }
        public uint VirtualSize { get { return (uint)RawData.Count; } }
        public uint VirtualAddress { get; private set; }
        public List<byte> RawData { get; private set; }
        public List<Relocation> Relocations { get; private set; }
        public List<object> LineNumbers { get; private set; }
        public SectionHeaderFlags Characteristics { get; private set; }
    }
}
