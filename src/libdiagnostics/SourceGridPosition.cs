using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
	/// <summary>
	/// Represents source code on a given line and at a given offset.
	/// </summary>
	public struct SourceGridPosition
	{
		public SourceGridPosition(int Line, int Offset)
        {
            this = default(SourceGridPosition);
            this.Line = Line;
            this.Offset = Offset;
        }
	
		public int Line { get; private set; }
		public int Offset { get; private set; }	
	}
}
