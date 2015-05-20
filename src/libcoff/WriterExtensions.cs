using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public static class WriterExtensions
    {
        public static void Write(this BinaryWriter writer, IReadOnlyList<byte> data)
        {
            writer.Write(data.ToArray());
        }

        public static void WriteAt(this BinaryWriter writer, long position, long value)
        {
            var oldPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = position;
            writer.Write(value);
            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, long position, ulong value)
        {
            var oldPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = position;
            writer.Write(value);
            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, long position, int value)
        {
            var oldPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = position;
            writer.Write(value);
            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, long position, uint value)
        {
            var oldPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = position;
            writer.Write(value);
            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, long position, float value)
        {
            var oldPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = position;
            writer.Write(value);
            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, long position, double value)
        {
            var oldPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = position;
            writer.Write(value);
            writer.BaseStream.Position = oldPosition;
        }

        /*public static void WriteAt(this BinaryWriter writer, IReadOnlyList<long> positions, long value)
        {
            var oldPosition = writer.BaseStream.Position;
            for (var i = 0; i < positions.Count; i++)
            {
                writer.BaseStream.Position = positions[i];
                writer.Write(value);
            }

            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, IReadOnlyList<long> positions, ulong value)
        {
            var oldPosition = writer.BaseStream.Position;
            for (var i = 0; i < positions.Count; i++)
            {
                writer.BaseStream.Position = positions[i];
                writer.Write(value);
            }

            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, IReadOnlyList<long> positions, int value)
        {
            var oldPosition = writer.BaseStream.Position;
            for (var i = 0; i < positions.Count; i++)
            {
                writer.BaseStream.Position = positions[i];
                writer.Write(value);
            }

            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, IReadOnlyList<long> positions, uint value)
        {
            var oldPosition = writer.BaseStream.Position;
            for (var i = 0; i < positions.Count; i++)
            {
                writer.BaseStream.Position = positions[i];
                writer.Write(value);
            }

            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, IReadOnlyList<long> positions, float value)
        {
            var oldPosition = writer.BaseStream.Position;
            for (var i = 0; i < positions.Count; i++)
            {
                writer.BaseStream.Position = positions[i];
                writer.Write(value);
            }

            writer.BaseStream.Position = oldPosition;
        }

        public static void WriteAt(this BinaryWriter writer, IReadOnlyList<long> positions, double value)
        {
            var oldPosition = writer.BaseStream.Position;
            for (var i = 0; i < positions.Count; i++)
            {
                writer.BaseStream.Position = positions[i];
                writer.Write(value);
            }

            writer.BaseStream.Position = oldPosition;
        }*/
    }
}
