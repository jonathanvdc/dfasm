using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public class StringTable
    {
        public StringTable()
        {
            buffer = new BinaryBuffer();
        }

        private BinaryBuffer buffer;

        public BinaryBuffer Buffer
        {
            get { return buffer; }
        }

        public void Clear()
        {
            buffer.Clear();
        }

        public string GetString(PeCoffName name)
        {
            if (name.Mode == PeCoffNameMode.ShortName)
            {
                var shortName = name.ShortName;
                int nullTerminator = Array.IndexOf(shortName, (byte)0);
                if (nullTerminator == -1) nullTerminator = shortName.Length;

                var bytes = ArrayOperations.Slice<byte>(shortName, 0, nullTerminator);
                var chars = Encoding.UTF8.GetChars(bytes);
                return new string(chars);
            }
            else if (name.Mode == PeCoffNameMode.OffsetToStringTable)
            {
                int offset = (int)name.Offset;
                if (offset < 0 || offset >= buffer.Length + 4)
                    throw new ArgumentException("name");

                return GetString((int)offset);
            }

            throw new ArgumentException("name");
        }

        public string GetString(int offset)
        {
            if (offset < 0 || offset >= buffer.Length + 4)
                throw new ArgumentOutOfRangeException("offset");

            offset -= 4;
            int end = buffer.IndexOf(0, offset);
            if (end == -1) end = buffer.Length;

            var data = buffer.ToArray(offset, end - offset);
            var chars = Encoding.UTF8.GetChars(data);
            return new string(chars);
        }

        public long AddLongString(string value)
        {
            char[] chars;
            if (value == null) chars = new char[0];
            else chars = value.ToCharArray();

            var bytes = Encoding.UTF8.GetBytes(chars);
            bytes = ArrayOperations.Concat(bytes, (byte)0);

            var offset = buffer.Length + 4;
            buffer.Append(bytes);
            return offset;
        }

        public PeCoffName AddString(string value)
        {
            char[] chars;
            if (value == null) chars = new char[0];
            else chars = value.ToCharArray();

            var bytes = Encoding.UTF8.GetBytes(chars);
            if (bytes.Length <= 8)
            {
                bytes = ArrayOperations.Resize<byte>(bytes, 8);
                return new PeCoffName(PeCoffNameMode.ShortName, bytes, 0);
            }

            bytes = ArrayOperations.Concat(bytes, (byte)0);

            var offset = buffer.Length + 4;
            buffer.Append(bytes);

            return new PeCoffName(
                PeCoffNameMode.OffsetToStringTable,
                null, checked((uint)offset));
        }

        public void WriteTo(BinaryWriter writer)
        {
            writer.Write(buffer.Length);
            writer.Write(buffer.ToArray());
        }

        public static StringTable ReadFrom(BinaryReader reader)
        {
            var ret = new StringTable();
            var length = reader.ReadInt32();
            ret.Buffer.Append(reader.ReadBytes(length));
            return ret;
        }
    }
}
