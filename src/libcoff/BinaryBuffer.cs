using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public sealed class BinaryBuffer
    {
        List<byte> data;

        public byte this[int i]
        {
            get
            {
                return data[i];
            }
        }

        public int Length
        {
            get { return data.Count; }
        }

        public byte[] ToArray(int position, int length)
        {
            if (position < 0 || position > length)
                throw new ArgumentOutOfRangeException("position");

            if (length < 0 || position + length > length)
                throw new ArgumentOutOfRangeException("length");

            return data.Skip(position).Take(length).ToArray();
        }

        public byte[] ToArray()
        {
            return data.ToArray();
        }

        public BinaryBuffer()
        {
            this.data = new List<byte>();
        }

        public void Append(BinaryBuffer value)
        {
            data.AddRange(value.data);
        }

        public void Append(byte value)
        {
            data.Add(value);
        }

        public void Append(sbyte value)
        {
            Append((byte)value);
        }

        public void Append(int value)
        {
            for (var i = 0; i < sizeof(int); i++)
            {
                Append((byte)value);
                value >>= 8;
            }
        }

        public void Append(ulong value, int size)
        {
            if (size <= 0)
                throw new ArgumentOutOfRangeException("size");

            for (var i = 0; i < size; i++)
            {
                Append((byte)value);
                value >>= 8;
            }

            if (value != 0)
            {
                throw new ArgumentException
                    ("The value doesn't fit into the specified size");
            }
        }

        public void Append(long value, int size)
        {
            if (size <= 0)
                throw new ArgumentOutOfRangeException("size");

            for (var i = 0; i < size - 1; i++)
            {
                Append((byte)value);
                value >>= 8;
            }

            var neededSign = value < 0;
            var currentSign = (value & 0x80) != 0;

            Append((byte)value);
            value >>= 8;

            if ((value != 0 && value != -1) || neededSign != currentSign)
            {
                throw new ArgumentException("The value doesn't fit into the specified size");
            }
        }

        public void Append(IReadOnlyList<byte> value)
        {
            data.AddRange(value);
        }

        public void Remove(int position, int length)
        {
            if (position < 0 || position > data.Count)
                throw new ArgumentOutOfRangeException("position");

            if (length < 0 || position + length > data.Count)
                throw new ArgumentOutOfRangeException("length");

            data.RemoveRange(position, length);
        }

        public void Clear()
        {
            data.Clear();
        }

        public void Insert(int position, IEnumerable<byte> values)
        {
            data.InsertRange(position, values);
        }

        public int IndexOf(byte value, int startPosition = 0)
        {
            return data.IndexOf(value, startPosition);
        }
    }
}
