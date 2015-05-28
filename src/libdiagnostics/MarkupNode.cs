using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    public struct MarkupNode
    {
        public MarkupNode(string Contents, bool IsHighlighted)
        {
            this = default(MarkupNode);
            this.Contents = Contents;
            this.IsHighlighted = IsHighlighted;
        }

        public string Contents { get; private set; }
        public bool IsHighlighted { get; private set; }
    }
}
