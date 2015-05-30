using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    [Serializable]
    public class DiagnosticsException : Exception
    {
        public DiagnosticsException(string Name, string Message, SourceLocation Location)
            : base(Message) { this.Entry = new LogEntry(Name, Message, Location); }
        public DiagnosticsException(LogEntry Entry) : base(Entry.Message) { this.Entry = Entry; }
        public DiagnosticsException(LogEntry Entry, Exception inner)
            : base(Entry.Message, inner) { this.Entry = Entry; }
        protected DiagnosticsException(
          System.Runtime.Serialization.SerializationInfo info,
          System.Runtime.Serialization.StreamingContext context)
            : base(info, context) { }

        public LogEntry Entry { get; private set; }
    }
}
