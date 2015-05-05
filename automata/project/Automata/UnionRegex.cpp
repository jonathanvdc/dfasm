#include "UnionRegex.h"

#include <memory>
#include <string>
#include <utility>
#include "ENFAutomaton.h"
#include "IRegex.h"
#include "LinearSet.h"
#include "Optional.h"
#include "RegexState.h"
#include "TransitionTable.h"
#include "HashExtensions.h"

using namespace Automata;

UnionRegex::UnionRegex(std::shared_ptr<IRegex> Left, std::shared_ptr<IRegex> Right)
{
    this->Left = Left;
    this->Right = Right;
}

ENFAutomaton<std::shared_ptr<RegexState>, std::string> UnionRegex::ToENFAutomaton() const
{
    auto startState = std::make_shared<RegexState>();
    TransitionTable<std::pair<std::shared_ptr<RegexState>, Optional<std::string>>, LinearSet<std::shared_ptr<RegexState>>> transTable;
    auto leftAutomaton = this->Left->ToENFAutomaton();
    auto rightAutomaton = this->Right->ToENFAutomaton();
    transTable.Add(leftAutomaton.getTransitionFunction());
    transTable.Add(rightAutomaton.getTransitionFunction());
    std::pair<std::shared_ptr<RegexState>, Optional<std::string>> label(startState, Optional<std::string>());
    LinearSet<std::shared_ptr<RegexState>> redirectedStates;
    redirectedStates.Add(leftAutomaton.getStartState());
    redirectedStates.Add(rightAutomaton.getStartState());
    transTable.Add(label, redirectedStates);
    auto acceptingStates = leftAutomaton.getAcceptingStates();
    acceptingStates.AddAll(rightAutomaton.getAcceptingStates());
    return ENFAutomaton<std::shared_ptr<RegexState>, std::string>(startState, acceptingStates, transTable);
}

std::string UnionRegex::ToString() const
{
    return this->Left->ToString() + "+" + this->Right->ToString();
}