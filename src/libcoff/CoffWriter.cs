using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    // libcoff is a derivative work of http://www.codeproject.com/Articles/705281/An-x-assembler-with-register-allocation,
    // licensed under the Code Project Open License (CPOL) (http://www.codeproject.com/info/cpol10.aspx)

    public static class CoffWriter
    {
        private static void WriteRelocs(BinaryWriter writer, IReadOnlyList<Relocation> relocations)
        {
            for (var i = 0; i < relocations.Count; i++)
            {
                var e = relocations[i];
                writer.Write(e.VirtualAddress);
                writer.Write(e.SymbolIndex);
                writer.Write((ushort)e.Type);
            }
        }

        public static void WriteToFile(string Path, ObjectFile File)
        {
            using (var fs = new FileStream(Path, FileMode.Create, FileAccess.Write))
            {
                WriteTo(fs, File);
            }
        }

        public static void WriteTo(Stream stream, ObjectFile file)
        {
            var stringTable = new StringTable();
            var writer = new BinaryWriter(stream);
            var coffPosition = stream.Position;

            var symbolCount = (uint)file.Symbols.Count;
            for (var i = 0; i < file.Symbols.Count; i++)
            {
                var e = file.Symbols[i];
                symbolCount += (uint)e.AuxiliarySymbols.Count;
            }

            writer.Write((ushort)file.Machine);
            writer.Write((ushort)file.Sections.Count);
            writer.Write((uint)0);
            var symbolTableReference = stream.Position;
            writer.Seek(4, SeekOrigin.Current);
            writer.Write(symbolCount);
            writer.Write((ushort)0);
            writer.Write((ushort)file.Characteristics);

            var sectionRawDataReferences = new long[file.Sections.Count];
            var sectionRelocationReferences = new long[file.Sections.Count];
            var sectionLinenumberReferences = new long[file.Sections.Count];

            for (var i = 0; i < file.Sections.Count; i++)
            {
                var e = file.Sections[i];
                var name = stringTable.AddString(e.Name);
                writer.Write(name.ToSectionName());
                writer.Write(e.VirtualSize);
                writer.Write(e.VirtualAddress);
                writer.Write(checked((uint)e.RawData.Count));

                var currentPosition = stream.Position;
                sectionRawDataReferences[i] = currentPosition;
                sectionRelocationReferences[i] = currentPosition + 4;
                sectionLinenumberReferences[i] = currentPosition + 8;
                writer.Seek(12, SeekOrigin.Current);

                writer.Write(checked((ushort)e.Relocations.Count));
                writer.Write(checked((ushort)e.LineNumbers.Count));
                writer.Write((uint)e.Characteristics);
            }

            var linenumberData = new byte[8];
            for (var i = 0; i < file.Sections.Count; i++)
            {
                var e = file.Sections[i];
                var position = stream.Position;
                writer.Write(e.RawData);
                writer.WriteAt(sectionRawDataReferences[i], checked((uint)position));

                position = stream.Position;
                WriteRelocs(writer, e.Relocations);
                writer.WriteAt(sectionRelocationReferences[i], checked((uint)position));

                position = stream.Position;
                writer.Write(linenumberData);
                writer.WriteAt(sectionLinenumberReferences[i], checked((uint)position));
            }

            var symbolTablePosition = stream.Position;
            writer.WriteAt(symbolTableReference, checked((uint)symbolTablePosition));

            for (var i = 0; i < file.Symbols.Count; i++)
            {
                var e = file.Symbols[i];
                var name = stringTable.AddString(e.Name);
                writer.Write(name.ToSymbolName());
                writer.Write(e.Value);

                int sectionNumber;
                if (e.Section == null)
                {
                    sectionNumber = 0;
                }
                else
                {
                    sectionNumber = file.GetSectionIndex(e.Section) + 1;
                    if (sectionNumber == -1) throw new ApplicationException();
                }

                writer.Write(checked((ushort)sectionNumber));
                e.Type.WriteTo(writer);
                writer.Write((byte)e.StorageClass);
                writer.Write((byte)e.AuxiliarySymbols.Count);

                foreach (var item in e.AuxiliarySymbols)
                {
                    item.WriteTo(writer);
                }
            }

            stringTable.WriteTo(writer);
        }
    }
}
