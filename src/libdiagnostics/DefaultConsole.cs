﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


namespace libdiagnostics
{
    public class DefaultConsole : ConsoleBase<DefaultConsoleStyle>
    {
        public DefaultConsole(int BufferWidth, Color ForegroundColor, Color BackgroundColor)
            : base(new DefaultConsoleStyle(ForegroundColor.Over(DefaultForegroundColor), BackgroundColor.Over(DefaultBackgroundColor)))
        {
            desc = new ConsoleDescription("default", BufferWidth, 
                InitialStyle.ForegroundColor, InitialStyle.BackgroundColor);
        }
        public DefaultConsole(int BufferWidth)
            : this(BufferWidth, new Color(), new Color())
        {
        }

        public static Color DefaultBackgroundColor
        {
            get
            {
                return ToPixieColor(Console.BackgroundColor);
            }
        }

        public static Color DefaultForegroundColor
        {
            get
            {
                return ToPixieColor(Console.ForegroundColor);
            }
        }

        private ConsoleDescription desc;

        public override ConsoleDescription Description
        {
            get { return desc; }
        }

        protected override DefaultConsoleStyle MergeStyles(DefaultConsoleStyle Source, Style Delta)
        {
            var fgColor = Delta.ForegroundColor.Over(Source.ForegroundColor);
            var bgColor = Delta.BackgroundColor.Over(Source.BackgroundColor);
            return new DefaultConsoleStyle(fgColor, bgColor);
        }

        protected override void ApplyStyle(DefaultConsoleStyle OldStyle, DefaultConsoleStyle Style)
        {
            Style.Apply();
        }

        public override void Dispose()
        {
            Console.ForegroundColor = ToConsoleColor(desc.ForegroundColor);
            Console.BackgroundColor = ToConsoleColor(desc.BackgroundColor);
        }

        #region Static

        public static int GetBufferWidth()
        {
            try
            {
                int result = Console.BufferWidth;
                return result > 0 ? result : 80;
            }
            catch (Exception)
            {
                return 80;
            }
        }

        static DefaultConsole()
        {
            consoleColorMapping = new Dictionary<ConsoleColor, Color>();

            consoleColorMapping.Add(ConsoleColor.Black,         new Color(0, 0, 0));
            consoleColorMapping.Add(ConsoleColor.DarkBlue,      new Color(0, 0, 0.5));
            consoleColorMapping.Add(ConsoleColor.DarkGreen,     new Color(0, 0.5, 0));
            consoleColorMapping.Add(ConsoleColor.DarkCyan,      new Color(0, 0.5, 0.5));
            consoleColorMapping.Add(ConsoleColor.DarkRed,       new Color(0.5, 0, 0));
            consoleColorMapping.Add(ConsoleColor.DarkMagenta,   new Color(0.5, 0, 0.5));
            consoleColorMapping.Add(ConsoleColor.DarkYellow,    new Color(0.5, 0.5, 0.0));
            consoleColorMapping.Add(ConsoleColor.Gray,          new Color(0.75, 0.75, 0.75));
            consoleColorMapping.Add(ConsoleColor.DarkGray,      new Color(0.5, 0.5, 0.5));
            consoleColorMapping.Add(ConsoleColor.Blue,          new Color(0.0, 0.0, 1.0));
            consoleColorMapping.Add(ConsoleColor.Cyan,          new Color(0.0, 1.0, 1.0));
            consoleColorMapping.Add(ConsoleColor.Green,         new Color(0.0, 1.0, 0.0));
            consoleColorMapping.Add(ConsoleColor.Red,           new Color(1.0, 0.0, 0.0));
            consoleColorMapping.Add(ConsoleColor.Magenta,       new Color(1.0, 0.0, 1.0));
            consoleColorMapping.Add(ConsoleColor.Yellow,        new Color(1.0, 1.0, 0.0));
            consoleColorMapping.Add(ConsoleColor.White,         new Color(1.0, 1.0, 1.0));
        }

        private static Dictionary<ConsoleColor, Color> consoleColorMapping;

        public static ConsoleColor ToConsoleColor(Color Value)
        {
            double bestDist = 3.0;
            ConsoleColor bestColor = ConsoleColor.White;
            foreach (var item in consoleColorMapping)
            {
                double distR = item.Value.Red - Value.Red;
                double distG = item.Value.Green - Value.Green;
                double distB = item.Value.Blue - Value.Blue;
                double dist = distR * distR + distG * distG + distB * distB;
                if (dist < bestDist)
                {
                    bestDist = dist;
                    bestColor = item.Key;
                    if (dist == 0.0)
                    {
                        break; // Return right now. It won't get any better than this.
                    }
                }
            }
            return bestColor;
        }
        public static Color ToPixieColor(ConsoleColor Color)
        {
            return consoleColorMapping[Color];
        }

        #endregion
    }
}
