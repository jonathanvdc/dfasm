using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace libjit
{
    public class VirtualBuffer : IDisposable
    {
        public VirtualBuffer(IntPtr Pointer)
        {
            this.Pointer = Pointer;
        }

        public IntPtr Pointer { get; private set; }

        public void Dispose()
        {
            VirtualFree(Pointer, 0, MEM_FREE);
        }

        public static VirtualBuffer Create(IEnumerable<byte> Data)
        {
            return Create(Data.ToArray());
        }
        public static VirtualBuffer Create(byte[] Data)
        {
            IntPtr buf = VirtualAlloc(IntPtr.Zero, (uint)Data.Length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
            Marshal.Copy(Data, 0, buf, Data.Length);
            return new VirtualBuffer(buf);
        }

        public const uint PAGE_EXECUTE_READWRITE = 0x40;
        public const uint MEM_COMMIT = 0x1000;
        public const uint MEM_FREE = 0x8000;

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool VirtualFree(IntPtr lpAddress, uint dwSize, uint dwFreeType);
    }
}
