using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    [Flags]
    public enum SectionHeaderFlags : uint
    {
        TypeNopad = 0x00000008,

        CntCode = 0x00000020,
        CntInitializedData = 0x00000040,
        CntUninitializedData = 0x00000080,
        LnkOther = 0x00000100,
        LnkInfo = 0x00000200,

        LnkRemove = 0x00000800,
        LnkComdat = 0x00001000,
        Gprel = 0x00008000,
        MemPurgeable = 0x00020000,
        Mem16bit = 0x00020000,
        MemLocked = 0x00040000,
        MemPreload = 0x00080000,
        Align1Bytes = 0x00100000,
        Align2Bytes = 0x00200000,
        Align4Bytes = 0x00300000,
        Align8Bytes = 0x00400000,
        Align16Bytes = 0x00500000,
        Align32Bytes = 0x00600000,
        Align64Bytes = 0x00700000,
        Align128Bytes = 0x00800000,
        Align256Bytes = 0x00900000,
        Align512Bytes = 0x00a00000,
        Align1024Bytes = 0x00b00000,
        Align2048Bytes = 0x00c00000,
        Align4096Bytes = 0x00d00000,
        Align8192Bytes = 0x00e00000,
        LnkNRelocOvfl = 0x01000000,
        MemDiscardable = 0x02000000,
        MemNotCached = 0x04000000,
        MemNotPaged = 0x08000000,
        MemShared = 0x10000000,
        MemExecute = 0x20000000,
        MemRead = 0x40000000,
        MemWrite = 0x80000000,
    }
}
