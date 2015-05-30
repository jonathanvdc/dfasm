using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public enum StorageClass : byte
    {
        EndOfFunction = 0xff,
        Null = 0,
        Automatic,
        External,
        Static,
        Register,
        ExternalDef,
        Label,
        UndefinedLabel,
        MemberOfStruct,
        Argument,
        StructTag,
        MemberOfUnion,
        UnionTag,
        TypeDefinition,
        UndefinedStatic,
        EnumTag,
        MemberOfEnum,
        RegisterParam,
        BitField,
        Block = 100,
        Function,
        EndOfStruct,
        File,
        Section,
        WeakExternal,
        ClrToken,
    }
}
