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
        public VirtualBuffer(IntPtr Pointer, uint Size)
        {
            this.Pointer = Pointer;
            this.Size = Size;
        }

        public IntPtr Pointer { get; private set; }
        public long Address { get { return (long)Pointer; } }
        public uint Size { get; private set; }

        public void Dispose()
        {
            VirtualFree(Pointer, 0, MEM_FREE);
        }

        public void Write(byte[] Data)
        {
            Marshal.Copy(Data, 0, Pointer, Data.Length);
        }

        public byte[] Read()
        {
            var data = new byte[Size];
            Marshal.Copy(Pointer, data, 0, (int)Size);
            return data;
        }

        public static VirtualBuffer Create(byte[] Data)
        {
            var buf = Create((uint)Data.Length);
            buf.Write(Data);
            return buf;
        }
        public static VirtualBuffer Create(uint Size)
        {
            IntPtr buf = VirtualAlloc(IntPtr.Zero, Size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
            return new VirtualBuffer(buf, Size);
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
