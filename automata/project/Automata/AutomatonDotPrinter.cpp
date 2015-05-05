#include "AutomatonDotPrinter.h"
#include <memory>
#include <iostream>
#include <string>
#include <locale>
#include "DFAutomaton.h"
#include "HashExtensions.h"

void AutomatonDotPrinter::Write(AutomatonDotPrinter::DFA Value, std::ostream& Output)
{
	// .dot header 
	Output << "digraph dfa {" << std::endl
		<< "    rankdir = LR;" << std::endl;

	// initial state arrow 
	Output << "    __start [style = invis, shape = point];" << std::endl
		<< "    __start -> \"" << Value.getStartState()
		<< "\" [ label = \"start\" ];" << std::endl;

	// mark final states 
	Output << "    node [shape = doublecircle];";
	for (State q : Value.getAcceptingStates().getItems())
		Output << " \"" << q << "\"";

	// draw transitions 
	Output << std::endl << "    node [shape = circle];" << std::endl;
	for (auto& p : Value.getTransitionFunction().getMap()) 
	{
		State from = p.first.first, to = p.second;
		Symbol sym = p.first.second;
		Output << "    \"" << from << "\" -> \"" << to
			<< "\" [ label = \"" << sym << "\" ];" << std::endl;

	}

	Output << "}" << std::endl;
}

void AutomatonDotPrinter::Write(AutomatonDotPrinter::NFA Value, std::ostream& Output)
{
	// .dot header 
	Output << "digraph nfa {" << std::endl
		<< "    rankdir = LR;" << std::endl;

	// initial state arrow 
	Output << "    __start [style = invis, shape = point];" << std::endl
		<< "    __start -> \"" << Value.getStartState()
		<< "\" [ label = \"start\" ];" << std::endl;

	// mark final states 
	Output << "    node [shape = doublecircle];";
	for (State q : Value.getAcceptingStates().getItems())
		Output << " \"" << q << "\"";

	// draw transitions 
	Output << std::endl << "    node [shape = circle];" << std::endl;
	for (auto& p : Value.getTransitionFunction().getMap())
	{
		State from = p.first.first;
		Symbol sym = p.first.second;
		for (auto& to : p.second.getItems())
		{
			Output << "    \"" << from << "\" -> \"" << to
				<< "\" [ label = \"" << sym << "\" ];" << std::endl;
		}
	}

	Output << "}" << std::endl;
}

void AutomatonDotPrinter::Write(AutomatonDotPrinter::ENFA Value, std::ostream& Output)
{
	// .dot header 
	Output << "digraph enfa {" << std::endl
		<< "    rankdir = LR;" << std::endl;

	// initial state arrow 
	Output << "    __start [style = invis, shape = point];" << std::endl
		<< "    __start -> \"" << Value.getStartState()
		<< "\" [ label = \"start\" ];" << std::endl;

	// mark final states 
	Output << "    node [shape = doublecircle];";
	for (State q : Value.getAcceptingStates().getItems())
		Output << " \"" << q << "\"";

	// draw transitions 
	Output << std::endl << "    node [shape = circle];" << std::endl;
	for (auto& p : Value.getTransitionFunction().getMap())
	{
		State from = p.first.first;
		std::string sym = p.first.second.HasValue ? p.first.second.Value : "&epsilon;";
		for (auto& to : p.second.getItems())
		{
			Output << "    \"" << from << "\" -> \"" << to
				<< "\" [ label = \"" << sym << "\" ];" << std::endl;
		}
	}

	Output << "}" << std::endl;
}