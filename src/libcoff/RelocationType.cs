using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public enum RelocationType : ushort
    {
        I386_ABSOLUTE = 0x0000,
        I386_DIR16 = 0x0001,
        I386_REL16 = 0x0002,
        I386_DIR32 = 0x0006,
        I386_DIR32NB = 0x0007,
        I386_SEG12 = 0x0009,
        I386_SECTION = 0x000a,
        I386_SECREL = 0x000b,
        I386_TOKEN = 0x000c,
        I386_SECREL7 = 0x000d,
        I386_REL32 = 0x0014,

        AMD64_ABSOLUTE = 0x0000,
        AMD64_ADDR64 = 0x0001,
        AMD64_ADDR32 = 0x0002,
        AMD64_ADDR32NB = 0x0003,
        AMD64_REL32 = 0x0004,
        AMD64_REL32_1 = 0x0005,
        AMD64_REL32_2 = 0x0006,
        AMD64_REL32_3 = 0x0007,
        AMD64_REL32_4 = 0x0008,
        AMD64_REL32_5 = 0x0009,
        AMD64_SECTION = 0x000a,
        AMD64_SECREL = 0x000b,
        AMD64_SECREL7 = 0x000c,
        AMD64_TOKEN = 0x000d,
        AMD64_SREL32 = 0x000e,
        AMD64_PAIR = 0x000f,
        AMD64_SSPAN32 = 0x0010,

        ARM_ABSOLUTE = 0x0000,
        ARM_ADDR32 = 0x0001,
        ARM_ADDR32NB = 0x0002,
        ARM_BRANCH24 = 0x0003,
        ARM_BRANCH11 = 0x0004,
        ARM_TOKEN = 0x0005,
        ARM_BLX24 = 0x0008,
        ARM_BLX11 = 0x0009,
        ARM_SECTION = 0x000e,
        ARM_SECREL = 0x000f,
        ARM_MOV32A = 0x0010,
        ARM_MOV32T = 0x0011,
        ARM_BRANCH20T = 0x0012,
        ARM_BRANCH24T = 0x0014,
        ARM_BLX23T = 0x0015,

        ARM64_ABSOLUTE = 0x0000,
        ARM64_ADDR32 = 0x0001,
        ARM64_ADDR32NB = 0x0002,
        ARM64_BRANCH26 = 0x0003,
        ARM64_PAGEBASE_REL21 = 0x0004,
        ARM64_REL21 = 0x0005,
        ARM64_PAGEOFFSET_12A = 0x0006,
        ARM64_PAGEOFFSET_12L = 0x0007,
        ARM64_SECREL = 0x0008,
        ARM64_SECREL_LOW12A = 0x0009,
        ARM64_SECREL_HIGH12A = 0x000a,
        ARM64_SECREL_LOW12L = 0x000b,
        ARM64_TOKEN = 0x000c,
        ARM64_SECTION = 0x000d,
        ARM64_ADDR64 = 0x000e,
    }
}
