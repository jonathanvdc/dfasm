#include "Interop.h"

#include <unordered_map>
#include <memory>
#include <iostream>
#include <cassert>
#include <string>
#include <set>
#include <sstream>
#include <fstream>
#include <sstream>
#include <msclr\marshal_cppstd.h>
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

	template<typename TState>
	State NameRegexState(TState State, std::unordered_map<TState, int>& Named)
	{
		auto iter = Named.find(State);
		if (Named.end() == iter) // Key not in dict
		{
			Named[State] = Named.size();
		}
		return Named[State];
	}

	template<typename TState>
	DFAutomaton<State, Symbol> RenameDFA(DFAutomaton<TState, Symbol> Automaton)
	{
		std::unordered_map<TState, int> names;
		auto setRenamer = Automata::LambdaFunction<TState, State>([&](TState state) { return NameRegexState(state, names); });
		IdFunction<Symbol> charRenamer;

		return Automaton.Rename<State, Symbol>(&setRenamer, &charRenamer);
	}

	DFAHandle::DFAHandle(Automata::DFAutomaton<State, Symbol> Automaton)
		: autom(new Automata::DFAutomaton<State, Symbol>(Automaton))
	{

	}

	DFAHandle::~DFAHandle()
	{
		delete autom;
	}

	Automata::DFAutomaton<State, Symbol>* DFAHandle::GetAutomaton()
	{
		return autom;
	}

	DFAState DFAHandle::GetInitialState()
	{
		return DFAState(this, autom->getStartState());
	}

	DFAState::DFAState(DFAHandle^ Automaton, int State)
		: autom(Automaton), state(State)
	{

	}

	bool DFAState::Accepts()
	{
		return autom->GetAutomaton()->IsAcceptingState(state);
	}

	DFAState DFAState::AddInput(System::String^ Data)
	{
		auto managed = state;
		int s = state;
		auto a = autom->GetAutomaton();
		for each (auto item in Data)
		{
			s = a->PerformTransition(s, std::string(1, (char)item));
		}
		return DFAState(autom, s);
	}

	DFAHandle^ Interop::CompileRegex(System::String^ Regex)
	{
		auto regexString = msclr::interop::marshal_as<std::string>(Regex);
		std::istringstream inputStream(regexString);
		RegexParser regexParser(inputStream);

		auto regex = regexParser.ParseRegex();

		auto enfa = regex->ToENFAutomaton();

		auto dfa = enfa.ToDFAutomaton();

		auto newDfa = dfa.Optimize();

		auto renamedDFa = RenameDFA(newDfa);

		return gcnew DFAHandle(renamedDFa);
	}
}