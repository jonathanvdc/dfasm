#include "EpsilonRegex.h"

#include <memory>
#include <string>
#include <unordered_map>
#include <utility>
#include "ENFAutomaton.h"
#include "IRegex.h"
#include "LinearSet.h"
#include "Optional.h"
#include "RegexState.h"
#include "TransitionTable.h"
#include "HashExtensions.h"

using namespace Automata;

EpsilonRegex::EpsilonRegex()
{ }

ENFAutomaton<std::shared_ptr<RegexState>, std::string> EpsilonRegex::ToENFAutomaton() const
{
    auto startState = std::make_shared<RegexState>();
    LinearSet<std::shared_ptr<RegexState>> acceptingStates;
    acceptingStates.Add(std::make_shared<RegexState>());
    std::unordered_map<std::pair<std::shared_ptr<RegexState>, Optional<std::string>>, LinearSet<std::shared_ptr<RegexState>>> transitions;
    std::pair<std::shared_ptr<RegexState>, Optional<std::string>> label(startState, Optional<std::string>());
    transitions[label] = acceptingStates;
    TransitionTable<std::pair<std::shared_ptr<RegexState>, Optional<std::string>>, LinearSet<std::shared_ptr<RegexState>>> transTable(transitions);
    return ENFAutomaton<std::shared_ptr<RegexState>, std::string>(startState, acceptingStates, transTable);
}

std::string EpsilonRegex::ToString() const
{
    return "\\e";
}