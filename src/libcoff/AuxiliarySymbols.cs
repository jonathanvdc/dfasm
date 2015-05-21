using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public interface IAuxiliarySymbol : IWritable
    {
        
    }

    public class AuxiliarySectionDefinition : IAuxiliarySymbol
    {
        public AuxiliarySectionDefinition(Section Target, ushort SectionIndex)
        {
            this.Target = Target;
            this.SectionIndex = SectionIndex;
        }

        public Section Target { get; private set; }
        public ushort SectionIndex { get; private set; }

        public uint Length { get { return checked((uint)Target.RawData.Count); } }
        public ushort RelocationCount { get { return checked((ushort)Target.Relocations.Count); } }
        public ushort LineNumberCount { get { return checked((ushort)Target.LineNumbers.Count); } }
        public uint Checksum { get { return 0; } }        

        public void WriteTo(BinaryWriter Writer)
        {
            Writer.Write(Length);
            Writer.Write(RelocationCount);
            Writer.Write(LineNumberCount);
            Writer.Write(0);
            Writer.Write(SectionIndex);
            Writer.Write((byte)0);
            Writer.Write((byte)0);
            Writer.Write((byte)0);
            Writer.Write((byte)0);
        }
    }

    public class AuxiliaryFileName : IAuxiliarySymbol
    {
        public AuxiliaryFileName(string Name)
        {
            this.Name = Name;
        }

        public string Name { get; private set; }
    
        public void WriteTo(BinaryWriter Writer)
        {
            var utf8Bytes = UTF8Encoding.UTF8.GetBytes(Name);
            var resizedBytes = ArrayOperations.Resize<byte>(utf8Bytes, 18);

            Writer.Write(resizedBytes);
        }
    }
}
