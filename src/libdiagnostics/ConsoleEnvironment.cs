using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    public static class ConsoleEnvironment
    {
        /// <summary>
        /// The environment variable name for the terminal identifier.
        /// </summary>
        public const string TerminalVariableName = "TERM";
        /// <summary>
        /// The xterm terminal identifier.
        /// </summary>
        public const string XTermIdentifier = "xterm";

        public static string OSVersionString
        {
            get
            {
                return Environment.OSVersion.VersionString;
            }
        }

        public static string TerminalIdentifier
        {
            get
            {
                return Environment.GetEnvironmentVariable(TerminalVariableName);
            }
        }

        public static bool IsXTerminalIdentifier(string Identifier)
        {
            return Identifier != null && (Identifier.Equals(XTermIdentifier, StringComparison.OrdinalIgnoreCase) || Identifier.StartsWith(XTermIdentifier + "-", StringComparison.OrdinalIgnoreCase));
        }

        public static bool IsVTerminal(string Identifier)
        {
            return Identifier != null && Identifier.StartsWith("vt", StringComparison.OrdinalIgnoreCase) && Identifier.Substring(2).All(char.IsDigit);
        }

        static ConsoleEnvironment()
        {
            registeredConsoles = new List<KeyValuePair<Func<string, bool>, Func<string, IConsole>>>();
            RegisterConsole(name => IsXTerminalIdentifier(name) || IsVTerminal(name),
                name => new AnsiConsole(name, DefaultConsole.GetBufferWidth()));
        }

        private static List<KeyValuePair<Func<string, bool>, Func<string, IConsole>>> registeredConsoles;

        public static void RegisterConsole(Func<string, bool> Predicate, Func<string, IConsole> Builder)
        {
            registeredConsoles.Add(new KeyValuePair<Func<string, bool>, Func<string, IConsole>>(Predicate, Builder));
        }

        public static IConsole AcquireConsole(string Identifier)
        {
            foreach (var item in registeredConsoles)
            {
                if (item.Key(Identifier))
                {
                    return item.Value(Identifier);
                }
            }
            return new DefaultConsole(DefaultConsole.GetBufferWidth());
        }
        public static IConsole AcquireConsole()
        {
            return AcquireConsole(TerminalIdentifier);
        }
    }
}
