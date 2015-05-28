﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    /// <summary>
    /// Describes an RGBA color.
    /// </summary>
    public struct Color
    {
        /// <summary>
        /// Creates a new color instance from the given channels.
        /// </summary>
        public Color(double Red, double Green, double Blue, double Alpha)
        {
            this = default(Color);
            this.Red = Red;
            this.Green = Green;
            this.Blue = Blue;
            this.Alpha = Alpha;
        }
        /// <summary>
        /// Creates a new color instance from the given RGB channels.
        /// Alpha is set to one.
        /// </summary>
        public Color(double Red, double Green, double Blue)
            : this(Red, Green, Blue, 1.0)
        {
        }
        /// <summary>
        /// Creates a new color instance from the given grayscale and alpha values.
        /// </summary>
        public Color(double Grayscale, double Alpha)
            : this(Grayscale, Grayscale, Grayscale, Alpha)
        {
        }
        /// <summary>
        /// Creates a new color instance from the given grayscale value.
        /// </summary>
        public Color(double Grayscale)
            : this(Grayscale, 1.0)
        {
        }

        /// <summary>
        /// Gets the color's alpha channel.
        /// </summary>
        public double Alpha { get; private set; }
        /// <summary>
        /// Gets the color's red channel.
        /// </summary>
        public double Red { get; private set; }
        /// <summary>
        /// Gets the color's green channel.
        /// </summary>
        public double Green { get; private set; }
        /// <summary>
        /// Gets the color's blue channel.
        /// </summary>
        public double Blue { get; private set; }

        /// <summary>
        /// Gets the color's grayscale intensity.
        /// </summary>
        public double Grayscale
        {
            get { return (Red + Green + Blue) / 3.0; }
        }

        /// <summary>
        /// Applies the "over" alpha blending operator to this color and the given
        /// other color.
        /// </summary>
        public Color Over(Color Other)
        {
            double otherAlpha = Other.Alpha * (1.0 - Alpha);
            double ao = Alpha + otherAlpha;
            double ro = Red * Alpha + Other.Red * otherAlpha;
            double go = Green * Alpha + Other.Green * otherAlpha;
            double bo = Blue * Alpha + Other.Blue * otherAlpha;
            return new Color(ro, go, bo, ao);
        }

        private void AppendChannel(StringBuilder sb, string Name, double Value)
        {
            sb.Append(Name);
            sb.Append(":");
            sb.Append(Value.ToString());
        }

        public override string ToString()
        {
            var sb = new StringBuilder();
            AppendChannel(sb, "a", Alpha);
            sb.Append(";");
            AppendChannel(sb, "r", Red);
            sb.Append(";");
            AppendChannel(sb, "g", Green);
            sb.Append(";");
            AppendChannel(sb, "b", Blue);
            return sb.ToString();
        }

        public static Color Parse(string Value)
        {
            string[] split = Value.Split(new char[] { ';' });
            double a = 1.0, r = 0.0, g = 0.0, b = 0.0;
            foreach (var item in split)
            {
                string[] splitElem = item.Split(new char[] { ':' });
                string key = splitElem[0].Trim(new char[] { });
                double val = double.Parse(splitElem[1].Trim(new char[] { }));

                if (key == "a" || key == "alpha") a = val;
                else if (key == "r" || key == "red") r = val;
                else if (key == "g" || key == "green") g = val;
                else if (key == "b" || key == "blue") b = val;
                else if (key == "gray" || key == "grey" || key == "grayscale" || key == "greyscale")
                {
                    r = val;
                    g = val;
                    b = val;
                }
            }
            return new Color(r, g, b, a);
        }
    }
}
