#include "PhiRegex.h"

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

PhiRegex::PhiRegex()
{ }

ENFAutomaton<std::shared_ptr<RegexState>, std::string> PhiRegex::ToENFAutomaton() const
{
    auto startState = std::make_shared<RegexState>();
    LinearSet<std::shared_ptr<RegexState>> acceptingStates;
    TransitionTable<std::pair<std::shared_ptr<RegexState>, Optional<std::string>>, LinearSet<std::shared_ptr<RegexState>>> transTable;
    return ENFAutomaton<std::shared_ptr<RegexState>, std::string>(startState, acceptingStates, transTable);
}

std::string PhiRegex::ToString() const
{
    return "\\p";
}