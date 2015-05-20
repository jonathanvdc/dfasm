using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public class CoffHeader
    {
        public CoffHeader()
        {

        }
        public CoffHeader(CoffHeader Other)
        {
            this.Machine = Other.Machine;
            this.NumberOfSections = Other.NumberOfSections;
            this.TimeDateStamp = Other.TimeDateStamp;
            this.PointerToSymbolTable = Other.PointerToSymbolTable;
            this.NumberOfSymbols = Other.NumberOfSymbols;
            this.SizeOfOptionalHeader = Other.SizeOfOptionalHeader;
            this.Characteristics = Other.Characteristics;
        }

        public const int Size = 20;

        public MachineType Machine;
        public ushort NumberOfSections;
        public uint TimeDateStamp;
        public uint PointerToSymbolTable;
        public uint NumberOfSymbols;
        public ushort SizeOfOptionalHeader;
        public CoffHeaderFlags Characteristics;

        public static CoffHeader ReadFrom(BinaryReader reader)
        {
            var ret = new CoffHeader();
            ret.Machine = (MachineType)reader.ReadUInt16();
            ret.NumberOfSections = reader.ReadUInt16();
            ret.TimeDateStamp = reader.ReadUInt32();
            ret.PointerToSymbolTable = reader.ReadUInt32();
            ret.NumberOfSymbols = reader.ReadUInt32();
            ret.SizeOfOptionalHeader = reader.ReadUInt16();
            ret.Characteristics = (CoffHeaderFlags)reader.ReadUInt16();
            return ret;
        }

        public void WriteTo(BinaryWriter writer)
        {
            writer.Write((ushort)Machine);
            writer.Write(NumberOfSections);
            writer.Write(TimeDateStamp);
            writer.Write(PointerToSymbolTable);
            writer.Write(NumberOfSymbols);
            writer.Write(SizeOfOptionalHeader);
            writer.Write((ushort)Characteristics);
        }
    }
}
