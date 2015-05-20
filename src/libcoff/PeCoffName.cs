using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public enum PeCoffNameMode : byte
    {
        Unknown,
        ShortName,
        OffsetToStringTable,
    }

    public struct PeCoffName
    {
        public PeCoffName(PeCoffNameMode mode, byte[] shortName, uint offset)
        {
            this = default(PeCoffName);
            if (mode == PeCoffNameMode.ShortName)
            {
                if (shortName == null)
                    throw new ArgumentNullException("shortName");

                if (shortName.Length > 8)
                {
                    throw new ArgumentException("The shortName is too long", "shortName");
                }
            }
            else if (mode == PeCoffNameMode.OffsetToStringTable)
            {
                if (offset > 9999999)
                {
                    throw new ArgumentException("The offset is too big", "offset");
                }
            }
            else
            {
                throw new ArgumentOutOfRangeException("mode");
            }

            this.Mode = mode;
            this.ShortName = shortName;
            this.Offset = offset;
        }

        public PeCoffNameMode Mode { get; private set; }
        public byte[] ShortName { get; private set; }
        public uint Offset { get; private set; }

        public static PeCoffName FromSymbolName(byte[] bytes)
        {
            if (bytes == null)
                throw new ArgumentNullException("bytes");

            if (bytes.Length != 8)
            {
                throw new ArgumentException
                    ("The length of bytes must be  8");
            }

            if (bytes[0] == 0 && bytes[1] == 0 && bytes[2] == 0 && bytes[3] == 0)
            {
                var offset = bytes[4] | (bytes[5] << 8) |
                    (bytes[6] << 16) | (bytes[7] << 24);

                return new PeCoffName
                    (PeCoffNameMode.OffsetToStringTable, bytes, (uint)offset);
            }

            return new PeCoffName(PeCoffNameMode.ShortName, bytes, 0);
        }

        public static PeCoffName FromSectionName(byte[] bytes)
        {
            if (bytes == null)
                throw new ArgumentNullException("bytes");

            if (bytes.Length != 8)
            {
                throw new ArgumentException
                    ("The length of bytes must be  8");
            }

            var chars = Encoding.UTF8.GetChars(bytes);
            var nullTerminator = Array.IndexOf(chars, '\0');
            if (nullTerminator == -1)
                nullTerminator = chars.Length;

            var str = new string(chars, 0, nullTerminator);
            if (str.Length > 0 && str[0] == '/')
            {
                uint offset;
                if (uint.TryParse(str.Substring(1), out offset))
                {
                    return new PeCoffName(
                        PeCoffNameMode.OffsetToStringTable,
                        bytes, offset);
                }
            }

            return new PeCoffName(PeCoffNameMode.ShortName, bytes, 0);
        }

        public byte[] ToSymbolName()
        {
            if (Mode == PeCoffNameMode.ShortName)
            {
                return ShortName;
            }
            else if (Mode == PeCoffNameMode.OffsetToStringTable)
            {
                var bytes = new byte[8];
                bytes[4] = (byte)((Offset & 0x000000FF));
                bytes[5] = (byte)((Offset & 0x0000FF00) >> 8);
                bytes[6] = (byte)((Offset & 0x00FF0000) >> 16);
                bytes[7] = (byte)((Offset & 0xFF000000) >> 24);
                return bytes;
            }

            throw new InvalidOperationException();
        }

        public byte[] ToSectionName()
        {
            if (Mode == PeCoffNameMode.ShortName)
            {
                return ShortName;
            }
            else if (Mode == PeCoffNameMode.OffsetToStringTable)
            {
                var str = "/" + Offset.ToString();
                var bytes = Encoding.UTF8.GetBytes(str);
                if (bytes.Length > 8)
                    throw new ApplicationException();

                var arr = new byte[8];
                bytes.CopyTo(arr, 0);
                return arr;
            }

            throw new InvalidOperationException();
        }
    }
}
