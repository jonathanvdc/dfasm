#pragma once
#include <memory>
#include <iostream>
#include <string>
#include <locale>
#include <clocale>
#include "NFAutomaton.h"
#include "DFAutomaton.h"
#include "ENFAutomaton.h"

namespace Automata
{
	struct AutomatonDotPrinter
	{
		typedef std::string State;
		typedef std::string Symbol;
		typedef DFAutomaton<State, Symbol> DFA;
		typedef NFAutomaton<State, Symbol> NFA;
		typedef ENFAutomaton<State, Symbol> ENFA;
		typedef std::shared_ptr<IAutomaton<Symbol>> Automaton;

		void Write(DFA Value, std::ostream& Output);
		void Write(NFA Value, std::ostream& Output);
		void Write(ENFA Value, std::ostream& Output);
	};
}