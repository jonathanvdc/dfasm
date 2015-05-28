
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    public class SourceNodeWriter
    {
        public SourceNodeWriter(string Indentation, int MaxWidth)
        {
            this.Indentation = Indentation;
            this.MaxWidth = MaxWidth;
        }

        public int MaxWidth { get; private set; }
        public string Indentation { get; private set; }

        public static Style GetCaretHighlightStyle(IStylePalette Palette)
        {
            if (Palette.IsNamedStyle(StyleConstants.CaretHighlightStyleName))
            {
                return Palette.GetNamedStyle(StyleConstants.CaretHighlightStyleName);
            }
            else
            {
                return new Style(StyleConstants.CaretHighlightStyleName, Palette.MakeDimColor(new Color(0.0, 1.0, 0.0)), new Color());
            }
        }

        public static Style GetCaretMarkerStyle(IStylePalette Palette)
        {
            if (Palette.IsNamedStyle(StyleConstants.CaretMarkerStyleName))
            {
                return Palette.GetNamedStyle(StyleConstants.CaretMarkerStyleName);
            }
            else
            {
                return new Style(StyleConstants.CaretMarkerStyleName, Palette.MakeBrightColor(new Color(0.0, 1.0, 0.0)), new Color());
            }
        }

        public void Write(IEnumerable<MarkupNode> Nodes, IConsole Console, IStylePalette Palette)
        {
            var writer = new SourceNodeWriterState(Console, GetCaretMarkerStyle(Palette), GetCaretHighlightStyle(Palette), Indentation, MaxWidth, Palette);
            writer.Write(Nodes);
        }
    }

    public class SourceNodeWriterState
    {
        public SourceNodeWriterState(IConsole Console, Style CaretStyle, Style HighlightStyle, string Indentation, int MaxWidth, IStylePalette Palette)
        {
            this.Console = Console;
            this.CaretStyle = CaretStyle;
            this.HighlightStyle = HighlightStyle;
            this.Indentation = Indentation;
            this.MaxWidth = MaxWidth;
            this.caretConsole = new IndirectConsole(Console.Description);
            this.Palette = Palette;
            this.width = 0;
            this.CaretCharacter = '^';
            this.UnderlineCharacter = '~';
        }

        public IConsole Console { get; private set; }
        public int MaxWidth { get; private set; }
        public string Indentation { get; private set; }
        public Style CaretStyle { get; private set; }
        public Style HighlightStyle { get; private set; }
        public IStylePalette Palette { get; private set; }

        public char CaretCharacter { get; private set; }
        public char UnderlineCharacter { get; private set; }

        private IndirectConsole caretConsole;
        private int width;

        private void FlushLine(bool AppendWhitespace)
        {
            if (!caretConsole.IsWhitespace)
            {
                Console.WriteLine();
                Console.Write(Indentation);
                Console.PushStyle(HighlightStyle);
                caretConsole.Flush(Console);
                Console.PopStyle();
            }
            else
            {
                caretConsole.Clear();
                if (AppendWhitespace)
                {
                    Console.WriteLine();
                }
            }
            width = 0;
        }

        private bool FlushLine(char Value, int CharacterWidth)
        {
            FlushLine(false);
            if (char.IsWhiteSpace(Value))
            {
                return false;
            }
            else
            {
                Console.WriteLine();
                Console.Write(Indentation);
                width = CharacterWidth;
                return true;
            }
        }

        private bool PrepareWrite(char Value)
        {
            if (width == 0)
            {
                if (char.IsWhiteSpace(Value))
                {
                    return false;
                }
                else
                {
                    Console.WriteLine();
                    Console.Write(Indentation);
                }
            }
            return true;
        }

        private void Write(MarkupNode Node, bool UseCaret, bool CaretStarted)
        {
            if (Node.IsHighlighted)
            {
                UseCaret = true;
                CaretStarted = false;
            }
            string nodeText = Node.Contents;
            foreach (var item in nodeText)
            {
                if (!PrepareWrite(item))
                {
                    continue;
                }

                int itemWidth = item == '\t' ? 4 : 1;
                width += itemWidth;
                if (width >= MaxWidth)
                {
                    if (!FlushLine(item, itemWidth))
                    {
                        continue;
                    }
                }

                if (!CaretStarted && UseCaret)
                {
                    caretConsole.Write(CaretCharacter.ToString(), CaretStyle);
                    if (item == '\t')
                    {
                        caretConsole.Write(new string(UnderlineCharacter, 3));
                    }
                    CaretStarted = true;
                }
                else if (UseCaret)
                {
                    caretConsole.Write(new string(UnderlineCharacter, item != '\t' ? 1 : 4));
                }
                else
                {
                    caretConsole.Write(item != '\t' ? " " : new string(' ', 4));
                }
                if (item == '\t')
                {
                    Console.Write(new string(' ', 4));
                }
                else
                {
                    Console.Write(item);
                }

            }
        }

        public void Write(IEnumerable<MarkupNode> Nodes)
        {
            Console.WriteLine();
            foreach (var item in Nodes)
            {
                Write(item, false, false);
            }            
            FlushLine(true);
        }
    }
}
