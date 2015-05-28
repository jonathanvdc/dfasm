using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libdiagnostics
{
	/// <summary>
	/// A source document implementation.
	/// </summary>
	public class SourceDocument
	{
		public SourceDocument(string Source, string Identifier)
        {
            this.Source = Source;
            this.Identifier = Identifier;
        }

		/// <summary>
		/// Gets the source document's identifier.
		/// </summary>
		public string Identifier { get; private set; }

		/// <summary>
		/// Gets the source document's source code.
		/// </summary>
		public string Source { get; private set; }

		private string[] lines;
		private string[] SourceLines
		{
			get
			{
				if (lines == null)
				{
					lines = Source.Split(new char[] { '\n' });
				}
				return lines;
			}
		}

		/// <summary>
		/// Gets the line count of this source document.
		/// </summary>
		public int LineCount
		{
			get { return SourceLines.Length; }
		}

		/// <summary>
		/// Gets the number of characters in the source file.
		/// </summary>
		public int CharacterCount
		{
            get { return Source.Length; }
		}

		/// <summary>
		/// Gets the source line with the given index.
		/// </summary>
		public string GetLine(int Index)
		{
			return SourceLines[Index];
		}

		/// <summary>
		/// Converts a source code character index to a grid position.
		/// </summary>
		public SourceGridPosition ToGridPosition(int CharacterIndex)
		{
			if (CharacterIndex < 0 || CharacterIndex >= CharacterCount)
			{
				return new SourceGridPosition(-1, -1);
			}

			string[] lines = SourceLines;

			int sum = lines[0].Length + 1;
			int prevSum = 0;
			int i = 0;
			while (CharacterIndex >= sum)
			{
				prevSum = sum;
				i++;
				sum += lines[i].Length + 1;
			}

			return new SourceGridPosition(i, CharacterIndex - prevSum);
		}
	}
}
