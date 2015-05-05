#include "DFAutomaton.h"
#include "NFAutomaton.h"
#include "ENFAutomaton.h"
#include "ArraySlice.h"
#include "TransitionTable.h"
#include "AutomatonParser.h"
#include "HashExtensions.h"
#include "LambdaFunction.h"
#include "RegexParser.h"

namespace Automata
{
	typedef int State;
	typedef std::string Symbol;

	typedef DFAutomaton<State, Symbol> DFA;
	typedef NFAutomaton<State, Symbol> NFA;

	value struct DFAState;

	public ref class DFAHandle
	{
	public:
		DFAHandle(Automata::DFAutomaton<State, Symbol> Automaton);
		~DFAHandle();

		Automata::DFAutomaton<State, Symbol>* GetAutomaton();

		DFAState GetInitialState();

	private:
		Automata::DFAutomaton<State, Symbol>* autom;
	};

	public value struct DFAState
	{
	public:
		DFAState(DFAHandle^ Automaton, int State);

		bool Accepts();

		DFAState AddInput(System::String^ Data);

	private:
		DFAHandle^ autom;
		int state;
	};

	public ref class Interop abstract sealed
	{
	public:
		static DFAHandle^ CompileRegex(System::String^ Regex);
	};
}