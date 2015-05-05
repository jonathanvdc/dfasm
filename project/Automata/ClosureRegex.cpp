#include <memory>
#include <string>
#include <utility>
#include "IRegex.h"
#include "ENFAutomaton.h"
#include "RegexState.h"
#include "TransitionTable.h"
#include "Optional.h"
#include "LinearSet.h"
#include "ClosureRegex.h"
#include "HashExtensions.h"

using namespace Automata;

std::string ClosureRegex::ToString() const
{
	if( this->Regex->ToString().size() == 1){
		return this->Regex->ToString() + "*";
	}
    return "(" + this->Regex->ToString() + ")*";
}

ENFAutomaton<std::shared_ptr<RegexState>, std::string> ClosureRegex::ToENFAutomaton() const
{
    TransitionTable<std::pair<std::shared_ptr<RegexState>, Optional<std::string>>, LinearSet<std::shared_ptr<RegexState>>> transTable;
    auto innerAutomaton = this->Regex->ToENFAutomaton();
    transTable.Add(innerAutomaton.getTransitionFunction());
    auto startState = std::make_shared<RegexState>();
    auto endState = std::make_shared<RegexState>();
    std::pair<std::shared_ptr<RegexState>, Optional<std::string>> label(startState, Optional<std::string>());
    LinearSet<std::shared_ptr<RegexState>> starTrans;
    starTrans.Add(innerAutomaton.getStartState());
    starTrans.Add(endState);
    transTable.Add(label, starTrans);
    auto innerEndStates = innerAutomaton.getAcceptingStates();
    for (auto& item : innerEndStates.getItems())
    {
        std::pair<std::shared_ptr<RegexState>, Optional<std::string>> pipeLabel(item, Optional<std::string>());
        transTable.Add(pipeLabel, starTrans);
    }
    LinearSet<std::shared_ptr<RegexState>> acceptingStates;
    acceptingStates.Add(endState);
    return ENFAutomaton<std::shared_ptr<RegexState>, std::string>(startState, acceptingStates, transTable);
}

ClosureRegex::ClosureRegex(std::shared_ptr<IRegex> Regex)
{
    this->Regex = Regex;
}