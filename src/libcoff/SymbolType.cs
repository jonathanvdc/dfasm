using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public struct SymbolType
    {
        public SymbolType(SymbolBaseType baseType, SymbolComplexType complexType)
        {
            this = default(SymbolType);
            this.BaseType = baseType;
            this.ComplexType = complexType;
        }

        public SymbolBaseType BaseType { get; set; }
        public SymbolComplexType ComplexType { get; set; }

        public void WriteTo(BinaryWriter writer)
        {
            writer.Write((byte)BaseType);
            writer.Write((byte)ComplexType);
        }

        public static SymbolType ReadFrom(BinaryReader reader)
        {
            var ret = new SymbolType();
            ret.BaseType = (SymbolBaseType)reader.ReadByte();
            ret.ComplexType = (SymbolComplexType)reader.ReadByte();
            return ret;
        }
    }
}
