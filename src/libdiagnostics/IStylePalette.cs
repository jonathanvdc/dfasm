
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    public interface IStylePalette
    {
        Style GetNamedStyle(string Name);
        bool IsNamedStyle(string Name);

        Color MakeBrightColor(Color Value);
        Color MakeDimColor(Color Value);
    }
}
