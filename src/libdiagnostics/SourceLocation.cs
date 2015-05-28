using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
    /// <summary>
    /// Defines a region of text in a source document.
    /// </summary>
    public class SourceLocation
    {
        /// <summary>
        /// Creates a new source location from the given document.
        /// </summary>
        public SourceLocation(SourceDocument Document)
        {
            this.Document = Document;
            this.Position = -1;
            this.Length = 0;
        }
        /// <summary>
        /// Creates a new source location from the given document and position.
        /// </summary>
        public SourceLocation(SourceDocument Document, int Position)
        {
            this.Document = Document;
            this.Position = Position;
            this.Length = 0;
        }
        /// <summary>
        /// Creates a new source location from the given document, position and length.
        /// </summary>
        public SourceLocation(SourceDocument Document, int Position, int Length)
        {
            this.Document = Document;
            this.Position = Position;
            this.Length = Length;
        }

        /// <summary>
        /// Gets the source document this source location is associated with.
        /// </summary>
        public SourceDocument Document { get; private set; }
        /// <summary>
        /// Gets the position in the source document.
        /// </summary>
        public int Position { get; private set; }
        /// <summary>
        /// Gets the source location's length.
        /// </summary>
        public int Length { get; private set; }

        /// <summary>
        /// Finds out if this source location actually identifies a location,
        /// instead of only specifying a source document.
        /// </summary>
        public bool HasLocation { get { return Position > 0 && Length > 0; } }

        /// <summary>
        /// Gets the source location's position in the source document's row-column grid.
        /// </summary>
        public SourceGridPosition GridPosition
        {
            get { return Document.ToGridPosition(Position); }
        }

        public IEnumerable<MarkupNode> CreateSourceNodes()
        {
            var gridPos = GridPosition;
            if (gridPos.Line < 0)
            {
                return new MarkupNode[] { };
            }

            return CreateSourceNodes(Document, gridPos, Length);
        }

        public static IEnumerable<MarkupNode> CreateSourceNodes(SourceDocument doc, SourceGridPosition gridPos, int Length)
        {
            string lineText = doc.GetLine(gridPos.Line);
            int offset = gridPos.Offset;
            int length = Math.Min(Length, lineText.Length - offset);
            var preTextNode = new MarkupNode(lineText.Substring(0, offset), false);
            string highlightedText = lineText.Substring(offset, length);
            if (string.IsNullOrWhiteSpace(highlightedText))
            {
                highlightedText = " "; // Make sure we have at least a whitespace
                // character to highlight.
            }
            var highlightTextNode = new MarkupNode(highlightedText, true);
            var postTextNode = new MarkupNode(lineText.Substring(offset + length), false);

            return new MarkupNode[] { preTextNode, highlightTextNode, postTextNode };
        }
    }
}
