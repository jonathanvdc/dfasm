
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    /// <summary>
    /// Describes a console.
    /// </summary>
    public struct ConsoleDescription
    {
        public ConsoleDescription(string Name, int BufferWidth, Color ForegroundColor, Color BackgroundColor)
        {
            this = default(ConsoleDescription);
            this.Name = Name;
            this.BufferWidth = BufferWidth;
            this.ForegroundColor = ForegroundColor;
            this.BackgroundColor = BackgroundColor;
        }

        public string Name { get; private set; }
        public int BufferWidth { get; private set; }
        public Color BackgroundColor { get; private set; }
        public Color ForegroundColor { get; private set; }
    }
}
