using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public enum SymbolBaseType : byte
    {
        /// <summary>
        /// No type information or unknown base type.
        /// </summary>
        Null = 0,
        /// <summary>
        /// Used with void pointers and functions.
        /// </summary>
        Void = 1,
        /// <summary>
        /// A character (signed byte).
        /// </summary>
        Char = 2,
        /// <summary>
        /// A 1-byte signed integer.
        /// </summary>
        Int8 = Char,
        /// <summary>
        /// A 2-byte signed integer.
        /// </summary>
        Short = 3,
        /// <summary>
        /// A 2-byte signed integer.
        /// </summary>
        Int16 = Short,
        /// <summary>
        /// A natural integer type on the target.
        /// </summary>
        Int = 4,
        /// <summary>
        /// A 4-byte signed integer.
        /// </summary>
        Long = 5,
        /// <summary>
        /// A 4-byte signed integer.
        /// </summary>
        Int32 = Long,
        /// <summary>
        /// A 4-byte floating-point number.
        /// </summary>
        Float = 6,
        /// <summary>
        /// An 8-byte floating-point number.
        /// </summary>
        Double = 7,
        /// <summary>
        /// A struct.
        /// </summary>
        Struct = 8,
        /// <summary>
        /// A union.
        /// </summary>
        Union = 9,
        /// <summary>
        /// An enumerated type.
        /// </summary>
        Enum = 10,
        /// <summary>
        /// A member of enumeration (a specific value).
        /// </summary>
        MemberOfEnumeration = 11,
        /// <summary>
        /// An unsigned byte.
        /// </summary>
        Byte = 12,
        /// <summary>
        /// A 1-byte unsigned integer.
        /// </summary>
        UInt8 = Byte,
        /// <summary>
        /// An unsigned 2-byte integer.
        /// </summary>
        Word = 13,
        /// <summary>
        /// An unsigned 2-byte integer.
        /// </summary>
        UInt16 = Word,
        /// <summary>
        /// An unsigned integer of natural size.
        /// </summary>
        UInt = 14,
        /// <summary>
        /// An unsigned 4-byte integer.
        /// </summary>
        DWord = 15,
        /// <summary>
        /// An unsigned 4-byte integer.
        /// </summary>
        UInt32 = DWord
    }
}
