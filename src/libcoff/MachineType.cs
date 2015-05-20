using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public enum MachineType : ushort
    {
        Unknown = 0x0,
        AM33 = 0x1d3,
        Amd64 = 0x8664,
        Arm = 0x1c0,
        ArmNT = 0x1c4,
        Arm64 = 0xaa64,
        Ebc = 0xebc,
        I386 = 0x14c,
        IA64 = 0x200,
        M32R = 0x9041,
        Mips16 = 0x266,
        MipsFPU = 0x366,
        MipsFPU16 = 0x466,
        PowerPC = 0x1f0,
        PowerPCFP = 0x1f1,
        R4000 = 0x166,
        SH3 = 0x1a2,
        SH3DSP = 0x1a3,
        SH4 = 0x1a6,
        SH5 = 0x1a8,
        Thumb = 0x1c2,
        WceMipsV2 = 0x169,
    }
}
