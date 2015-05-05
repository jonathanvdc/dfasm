// Automata.cpp : Defines the entry point for the console application.
//

#include <unordered_map>
#include <memory>
#include <iostream>
#include <cassert>
#include <string>
#include <set>
#include <sstream>
#include <fstream>
#include "DFAutomaton.h"
#include "NFAutomaton.h"
#include "ENFAutomaton.h"
#include "ArraySlice.h"
#include "TransitionTable.h"
#include "AutomatonParser.h"
#include "HashExtensions.h"
#include "LambdaFunction.h"
#include "AutomatonDotPrinter.h"
#include "RegexParser.h"

#include "DFAtoRE.h"

typedef std::string State;
typedef std::string Symbol;

typedef Automata::DFAutomaton<State, Symbol> DFA;
typedef Automata::NFAutomaton<State, Symbol> NFA;

State NameSets(LinearSet<State> vals)
{
	auto valsVec = vals.getItems();
	std::set<State> states(valsVec.begin(), valsVec.end());
	std::ostringstream result;
	result << "{";
	bool first = true;
	for (auto& item : states)
	{
		if (!first)
		{
			result << ",";
		}
		first = false;
		result << item;
	}
	result << "}";
	return result.str();
}

State NameRegexState(std::shared_ptr<RegexState> State, std::unordered_map<std::shared_ptr<RegexState>, int>& Named)
{
	auto iter = Named.find(State);
	if (Named.end() == iter) // Key not in dict
	{
		Named[State] = Named.size();
	}
	std::ostringstream ss;
	ss << Named[State];
	return ss.str();
}

int main(int argc, const char* argv[])
{
	if (argc < 2)
	{
		std::cout << "No arguments have been specified. Give me something to do:" << std::endl;
		std::cout << " * ssc <input file>.nfa <output file>.dfa (NFA->DFA conversion)" << std::endl;
		std::cout << " * mssc <input file>.enfa <output file>.dfa (e-NFA->DFA conversion)" << std::endl;
		std::cout << " * accepts <input file> <string> (test a string)" << std::endl;
		std::cout << " * dot <input file>.dfa <target file>.dot (gets a dot language representation)" << std::endl;
		std::cout << " * re2enfa <input file>.re <target file>.enfa (regex->e-NFA conversion)" << std::endl;
		std::cout << " * dfa2re <input file>.dfa <target file>.re (DFA->regex conversion)" << std::endl;
		std::cout << " * nfa2re <input file>.nfa <target file>.re (NFA->regex conversion)" << std::endl;
		std::cout << " * partition <input file>.dfa (show sets of equivalent states)" << std::endl;
		std::cout << " * optimize <input file>.dfa <output file>.dfa (DFA optimization)" << std::endl;
		std::cout << " * equivalent <input file A>.dfa <input file B>.dfa (DFA equivalence)" << std::endl;
		return 0;
	}

	AutomatonParser parser;

	std::ifstream input(argv[2]);

	if (!input)
	{
		std::cout << "Input file '" << argv[2] << "' could not be opened." << std::endl;
		return 0;
	}

	if (std::string(argv[1]) == "dot")
	{
		auto type = parser.ReadType(input);

		AutomatonDotPrinter printer;

		std::ofstream output(argv[3]);

		if (type == parser.Deterministic)
		{
			printer.Write(parser.ReadDFAutomaton(input), output);
		}
		else if (type == parser.NonDeterministic)
		{
			printer.Write(parser.ReadNFAutomaton(input), output);
		}
		else
		{
			printer.Write(parser.ReadENFAutomaton(input), output);
		}
	}
	else if (std::string(argv[1]) == "ssc")
	{
		auto nfa = parser.ReadNFAutomaton(input);
		input.close();
		auto dfa = nfa.ToDFAutomaton();

		auto setRenamer = Automata::LambdaFunction<LinearSet<State>, State>(NameSets);
		IdFunction<Symbol> charRenamer;

		auto renamedDfa = dfa.Rename(&setRenamer, &charRenamer);

		std::ofstream output(argv[3]);

		parser.Write(renamedDfa, output);

		output.close();
	}
	else if (std::string(argv[1]) == "mssc")
	{
		auto enfa = parser.ReadENFAutomaton(input);
		input.close();
		auto dfa = enfa.ToDFAutomaton();

		auto setRenamer = Automata::LambdaFunction<LinearSet<State>, State>(NameSets);
		IdFunction<Symbol> charRenamer;

		auto renamedDfa = dfa.Rename(&setRenamer, &charRenamer);

		std::ofstream output(argv[3]);

		parser.Write(renamedDfa, output);

		output.close();
	}
	else if (std::string(argv[1]) == "re2enfa")
	{
		RegexParser regexParser(input);

		auto regex = regexParser.ParseRegex();
		input.close();

		auto enfa = regex->ToENFAutomaton();

		std::unordered_map<std::shared_ptr<RegexState>, int> names;
		auto setRenamer = Automata::LambdaFunction<std::shared_ptr<RegexState>, State>([&](std::shared_ptr<RegexState> state) { return NameRegexState(state, names); });
		IdFunction<Symbol> charRenamer;

		auto renamedEnfa = enfa.Rename<State, Symbol>(&setRenamer, &charRenamer);

		std::ofstream output(argv[3]);

		parser.Write(renamedEnfa, output);

		output.close();
	}
	else if (std::string(argv[1]) == "dfa2re")
	{
		auto dfa = parser.ReadDFAutomaton(input);
		input.close();

		auto regex = DFAtoRE(dfa);

		std::ofstream output(argv[3]);

		output << "Regex:\n";
		output << regex->ToString();

		output.close();
	}
	else if (std::string(argv[1]) == "partition")
	{
		auto dfa = parser.ReadDFAutomaton(input);
		std::cout << "The following sets of states are equivalent:" << std::endl;
		std::set<State> uniqueEntries;
		for (auto &item : dfa.TFAPartition())
			uniqueEntries.insert(NameSets(item.second));
		for (auto s : uniqueEntries)
			std::cout << "- " << s << std::endl;
	}
	else if (std::string(argv[1]) == "optimize")
	{
		auto dfa = parser.ReadDFAutomaton(input);
		auto newDfa = dfa.Optimize();

		auto setRenamer = Automata::LambdaFunction<LinearSet<State>, State>(NameSets);
		IdFunction<Symbol> charRenamer;

		auto renamedDfa = newDfa.Rename(&setRenamer, &charRenamer);

		std::ofstream output(argv[3]);

		parser.Write(renamedDfa, output);

		output.close();
	}
	else if (std::string(argv[1]) == "equivalent")
	{
		std::ifstream input2(argv[3]);
		if (!input2)
		{
			std::cout << "Input file '" << argv[3] << "' could not be opened." << std::endl;
			return 0;
		}

		auto dfa1 = parser.ReadDFAutomaton(input);
		auto dfa2 = parser.ReadDFAutomaton(input2);
		std::cout << "The given automata are ";
		if (!dfa1.EquivalentTo(dfa2)) std::cout << "not ";
		std::cout << "equivalent." << std::endl;
	}
	else if (std::string(argv[1]) == "nfa2re")
	{
		auto nfa = parser.ReadNFAutomaton(input);
		input.close();

		auto regex = NFAtoRE(nfa);

		std::ofstream output(argv[3]);

		output << "Regex:" << std::endl;
		output << regex->ToString() << std::endl;

		output.close();
	}
	else
	{
		auto automaton = parser.ReadAutomaton(input);

		std::vector<std::string> parsedString;
		for (char item : std::string(argv[3]))
		{
			parsedString.push_back(std::string(1, item));
		}

		if (automaton->Accepts(parsedString))
		{
			std::cout << "The automaton accepts the given string." << std::endl;
		}
		else
		{
			std::cout << "The automaton did not accept the given string." << std::endl;
		}
	}

	return 0;
}
