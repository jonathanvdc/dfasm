using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace libjit
{
    /// <summary>
    /// Defines a contiguous region of memory.
    /// </summary>
    public class VirtualBuffer : IDisposable
    {
        /// <summary>
        /// Creates a new virtual buffer handle structure from the given pointer and size.
        /// </summary>
        /// <param name="Pointer"></param>
        /// <param name="Size"></param>
        public VirtualBuffer(IntPtr Pointer, uint Size)
        {
            this.Pointer = Pointer;
            this.Size = Size;
        }

        /// <summary>
        /// Gets a pointer to the virtual buffer's base offset.
        /// </summary>
        public IntPtr Pointer { get; private set; }
        /// <summary>
        /// Gets the virtual buffer's size, in bytes.
        /// </summary>
        public uint Size { get; private set; }

        /// <summary>
        /// Frees the virtual buffer's memory region.
        /// </summary>
        public void Dispose()
        {
            VirtualFree(Pointer, 0, MEM_FREE);
        }

        /// <summary>
        /// Fills the virtual buffer with the data in the given array.
        /// </summary>
        /// <param name="Data"></param>
        public void Write(byte[] Data)
        {
            Marshal.Copy(Data, 0, Pointer, Data.Length);
        }

        /// <summary>
        /// Reads this virtual buffer's data into the given array.
        /// </summary>
        /// <returns></returns>
        public byte[] Read()
        {
            var data = new byte[Size];
            Marshal.Copy(Pointer, data, 0, (int)Size);
            return data;
        }

        /// <summary>
        /// Creates a virtual buffer with read/write/execute privileges
        /// of the same size as the given array, and fills it with the
        /// array's data.
        /// </summary>
        /// <param name="Data"></param>
        /// <returns></returns>
        public static VirtualBuffer Create(byte[] Data)
        {
            var buf = Create((uint)Data.Length);
            buf.Write(Data);
            return buf;
        }
        /// <summary>
        /// Creates a virtual buffer with read/write/execute privileges
        /// of the given size.
        /// </summary>
        /// <param name="Size"></param>
        /// <returns></returns>
        public static VirtualBuffer Create(uint Size)
        {
            IntPtr buf = VirtualAlloc(IntPtr.Zero, Size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
            return new VirtualBuffer(buf, Size);
        }

        /// <summary>
        /// The 'read/write/execute' memory privilege.
        /// </summary>
        public const uint PAGE_EXECUTE_READWRITE = 0x40;
        /// <summary>
        /// The 'commit memory' allocation type.
        /// </summary>
        public const uint MEM_COMMIT = 0x1000;
        /// <summary>
        /// The 'free memory' allocation type.
        /// </summary>
        public const uint MEM_FREE = 0x8000;

        /// <summary>
        /// Allocates a block of memory at the given address, of the given size, 
        /// based on the given allocation type and privileges.
        /// </summary>
        /// <param name="lpAddress"></param>
        /// <param name="dwSize"></param>
        /// <param name="flAllocationType"></param>
        /// <param name="flProtect"></param>
        /// <returns></returns>
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        /// <summary>
        /// Frees a block of memory at the given address, of the given size,
        /// with the given allocation type.
        /// </summary>
        /// <param name="lpAddress"></param>
        /// <param name="dwSize"></param>
        /// <param name="dwFreeType"></param>
        /// <returns></returns>
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool VirtualFree(IntPtr lpAddress, uint dwSize, uint dwFreeType);
    }
}
