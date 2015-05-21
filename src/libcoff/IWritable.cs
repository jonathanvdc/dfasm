using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public interface IWritable
    {
        void WriteTo(BinaryWriter Writer);
    }
}
