
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    public static class StyleConstants
    {
        public const string CaretMarkerStyleName = "caret-marker";
        public const string CaretHighlightStyleName = "caret-highlight";

        public static Style GetBrightStyle(IStylePalette Palette, string Name, Color ForegroundColor, params string[] Preferences)
        {
            if (Palette.IsNamedStyle(Name))
            {
                return Palette.GetNamedStyle(Name);
            }
            else
            {
                return new Style(Name, Palette.MakeBrightColor(ForegroundColor), new Color(), Preferences);
            }
        }
        public static Style GetDimStyle(IStylePalette Palette, string Name, Color ForegroundColor, params string[] Preferences)
        {
            if (Palette.IsNamedStyle(Name))
            {
                return Palette.GetNamedStyle(Name);
            }
            else
            {
                return new Style(Name, Palette.MakeDimColor(ForegroundColor), new Color(), Preferences);
            }
        }
    }
}
