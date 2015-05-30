using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    public class LogEntry
    {
        public LogEntry(string Name, string Message, SourceLocation Location)
        {
            this.Name = Name;
            this.Message = Message;
            this.Location = Location;
        }

        public string Name { get; private set; }
        public string Message { get; private set; }
        public SourceLocation Location { get; private set; }
    }

    public class ConsoleLog
    {
        public ConsoleLog(IConsole Console)
            : this(new ParagraphConsole(Console), CreateDefaultPalette(Console.Description))
        {

        }
        public ConsoleLog(IConsole Console, IStylePalette Palette)
        {
            this.Console = new ParagraphConsole(Console);
            this.Palette = Palette;
        }

        public ParagraphConsole Console { get; private set; }
        public IStylePalette Palette { get; private set; }

        #region WriteEntry

        public void WriteEntry(string Header, Color HeaderColor, Color PrimaryColor,
            Color SecondaryColor, LogEntry Entry)
        {
            if (!string.IsNullOrWhiteSpace(Header))
            {
                Console.Write(Header + ": ", HeaderColor);
            }
            WriteEntryInternal(PrimaryColor, SecondaryColor, Entry);
        }
        public void WriteEntry(string Header, Color PrimaryColor, Color SecondaryColor, LogEntry Entry)
        {
            WriteEntry(Header, PrimaryColor, PrimaryColor, SecondaryColor, Entry);
        }
        public void WriteEntry(LogEntry Entry)
        {
            WriteEntry("", BrightGreen, DimGreen, Entry);
        }

        public void WriteBlockEntry(string Header, Color HeaderColor, Color PrimaryColor,
            Color SecondaryColor, LogEntry Entry)
        {
            WriteEntry(Header, HeaderColor, PrimaryColor, SecondaryColor, Entry);
            Console.WriteSeparator(2);
        }
        public void WriteBlockEntry(string Header, Color PrimaryColor, Color SecondaryColor, LogEntry Entry)
        {
            WriteBlockEntry(Header, PrimaryColor, PrimaryColor, SecondaryColor, Entry);
        }

        private void WriteEntryInternal(Color PrimaryColor, Color SecondaryColor, LogEntry Entry)
        {
            string name = Entry.Name;
            if (!string.IsNullOrWhiteSpace(name))
            {
                Console.Write(name, ContrastForegroundColor);
                Console.Write(": ");
            }

            Console.Write(Entry.Message);

            var nodes = Entry.Location.CreateSourceNodes();

            var writer = new SourceNodeWriter(new string(' ', 4), Console.Description.BufferWidth);

            var dependentStyles = new List<Style>();
            dependentStyles.Add(new Style(StyleConstants.CaretMarkerStyleName, PrimaryColor, new Color()));
            dependentStyles.Add(new Style(StyleConstants.CaretHighlightStyleName, SecondaryColor, new Color()));

            var extPalette = new ExtendedPalette(Palette, dependentStyles);

            writer.Write(nodes, Console, extPalette);

            Console.WriteSeparator(1);

            Console.PushStyle(new Style("remark", DimGray, new Color()));
            Console.WriteLine("Remark: In '" + Entry.Location.Document.Identifier + "'.");
            Console.PopStyle();
        }

        #endregion

        #region Palette

        public static IStylePalette CreateDefaultPalette(ConsoleDescription Description)
        {
            return CreateDefaultPalette(Description.ForegroundColor, Description.BackgroundColor);
        }

        public static IStylePalette CreateDefaultPalette(Color ForegroundColor, Color BackgroundColor)
        {
            return new StylePalette(ForegroundColor, BackgroundColor);
        }

        #endregion

        #region Palette

        public Color ContrastForegroundColor
        {
            get
            {
                return StylePalette.MakeContrastColor(Console.Description.ForegroundColor,
                                                      Console.Description.BackgroundColor);
            }
        }

        public Color ForegroundColor
        {
            get
            {
                return Console.Description.ForegroundColor;
            }
        }

        public Color BackgroundColor
        {
            get
            {
                return Console.Description.BackgroundColor;
            }
        }

        public Color BrightRed
        {
            get
            {
                return Palette.MakeBrightColor(DefaultConsole.ToPixieColor(ConsoleColor.Red));
            }
        }

        public Color DimRed
        {
            get
            {
                return Palette.MakeDimColor(DefaultConsole.ToPixieColor(ConsoleColor.Red));
            }
        }

        public Color BrightYellow
        {
            get
            {
                return Palette.MakeBrightColor(DefaultConsole.ToPixieColor(ConsoleColor.Yellow));
            }
        }

        public Color DimYellow
        {
            get
            {
                return Palette.MakeDimColor(DefaultConsole.ToPixieColor(ConsoleColor.Yellow));
            }
        }

        public Color BrightBlue
        {
            get
            {
                return Palette.MakeBrightColor(DefaultConsole.ToPixieColor(ConsoleColor.Blue));
            }
        }

        public Color DimBlue
        {
            get
            {
                return Palette.MakeDimColor(DefaultConsole.ToPixieColor(ConsoleColor.Blue));
            }
        }

        public Color BrightCyan
        {
            get
            {
                return Palette.MakeBrightColor(DefaultConsole.ToPixieColor(ConsoleColor.Cyan));
            }
        }

        public Color DimCyan
        {
            get
            {
                return Palette.MakeDimColor(DefaultConsole.ToPixieColor(ConsoleColor.Cyan));
            }
        }

        public Color BrightMagenta
        {
            get
            {
                return Palette.MakeBrightColor(DefaultConsole.ToPixieColor(ConsoleColor.Magenta));
            }
        }

        public Color DimMagenta
        {
            get
            {
                return Palette.MakeDimColor(DefaultConsole.ToPixieColor(ConsoleColor.Magenta));
            }
        }

        public Color BrightGreen
        {
            get
            {
                return Palette.MakeBrightColor(DefaultConsole.ToPixieColor(ConsoleColor.Green));
            }
        }

        public Color DimGreen
        {
            get
            {
                return Palette.MakeDimColor(DefaultConsole.ToPixieColor(ConsoleColor.Green));
            }
        }

        public Color BrightGray
        {
            get
            {
                return Palette.MakeBrightColor(DefaultConsole.ToPixieColor(ConsoleColor.Gray));
            }
        }

        public Color DimGray
        {
            get
            {
                return Palette.MakeDimColor(DefaultConsole.ToPixieColor(ConsoleColor.Gray));
            }
        }

        #endregion

        public void LogError(LogEntry Entry)
        {
            WriteBlockEntry("Error", BrightRed, DimRed, Entry);
        }

        public void LogError(string Name, string Message, SourceLocation Location)
        {
            LogError(new LogEntry(Name, Message, Location));
        }

        public void LogWarning(LogEntry Entry)
        {
            WriteBlockEntry("Warning", BrightYellow, DimYellow, Entry);
        }

        public void LogWarning(string Name, string Message, SourceLocation Location)
        {
            LogWarning(new LogEntry(Name, Message, Location));
        }

        public void Dispose()
        {
            Console.Dispose();
        }
    }
}
