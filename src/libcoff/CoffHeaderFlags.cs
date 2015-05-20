using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    [Flags]
    public enum CoffHeaderFlags : ushort
    {
        RelocsStripped = 0x0001,
        ExecutableImage = 0x0002,
        LineNumbersStripped = 0x0004,
        LocalSymbolsStripped = 0x0008,
        AgressiveWSTrim = 0x0010,
        LargeAddressAware = 0x0020,
        BytesReservedLow = 0x0080,
        Machine32Bit = 0x0100,
        DebugStripped = 0x0200,
        RemovableRunFromSwap = 0x0400,
        NetRunFromSwap = 0x0800,
        System = 0x1000,
        Dll = 0x2000,
        UpSystemOnly = 0x4000,
        BytesReservedHigh = 0x8000,
    }
}
