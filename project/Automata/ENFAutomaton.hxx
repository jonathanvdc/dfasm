#include "ENFAutomaton.h"

#include <unordered_map>
#include <utility>
#include "ArraySlice.h"
#include "DFAutomaton.h"
#include "IAutomaton.h"
#include "IFunction.h"
#include "LinearSet.h"
#include "Optional.h"
#include "TransitionTable.h"

using namespace Automata;

template<typename TState, typename TChar>
ENFAutomaton<TState, TChar>::ENFAutomaton(TState StartState, LinearSet<TState> AcceptingStates, TransitionTable<std::pair<TState, Optional<TChar>>, LinearSet<TState>> TransitionFunction)
{
    this->setStartState(StartState);
    this->setAcceptingStates(AcceptingStates);
    this->setTransitionFunction(TransitionFunction);
}

/// \brief Gets a boolean value that indicates whether the automaton accepts the given string.
template<typename TState, typename TChar>
bool ENFAutomaton<TState, TChar>::Accepts(stdx::ArraySlice<TChar> Characters) const
{
    return this->ContainsAcceptingState(this->PerformExtendedTransition(this->getStartState(), Characters));
}

template<typename TState, typename TChar>
bool ENFAutomaton<TState, TChar>::ContainsAcceptingState(LinearSet<TState> States) const
{
    auto acceptStates = this->getAcceptingStates();
    auto intersection = acceptStates.Intersect(States);
    return !intersection.getIsEmpty();
}

template<typename TState, typename TChar>
LinearSet<TState> ENFAutomaton<TState, TChar>::Eclose(TState State) const
{
    LinearSet<TState> results;
    LinearSet<TState> step;
    step.Add(State);
    while (!step.getIsEmpty())
    {
        auto last = step.getLast();
        results.Add(last);
        step.RemoveLast();
        LinearSet<TState> nextStep;
        auto trans = this->PerformTransition(last, Optional<TChar>());
        for (auto& item : trans.getItems())
        {
            if (!results.Contains(item))
            {
                step.Add(item);
            }
        }
    }
    return results;
}

template<typename TState, typename TChar>
LinearSet<TState> ENFAutomaton<TState, TChar>::Eclose(LinearSet<TState> States) const
{
    LinearSet<TState> vals;
    for (auto& item : States.getItems())
    {
        vals.AddAll(this->Eclose(item));
    }
    return vals;
}

template<typename TState, typename TChar>
LinearSet<TChar> ENFAutomaton<TState, TChar>::GetAlphabet() const
{
    LinearSet<TChar> results;
    auto transfunc = this->getTransitionFunction();
    for (auto& item : transfunc.getMap())
    {
        if (item.first.second.HasValue)
        {
            results.Add(item.first.second.Value);
        }
    }
    return results;
}

template<typename TState, typename TChar>
LinearSet<TState> ENFAutomaton<TState, TChar>::GetStates() const
{
    LinearSet<TState> results;
    auto transfunc = this->getTransitionFunction();
    for (auto& item : transfunc.getMap())
    {
        results.Add(item.first.first);
        results.AddAll(item.second);
    }
    return results;
}

template<typename TState, typename TChar>
LinearSet<TState> ENFAutomaton<TState, TChar>::PerformAllTransitions(LinearSet<TState> States, Optional<TChar> Character) const
{
    LinearSet<TState> results;
    for (auto& val : States.getItems())
    {
        results.AddAll(this->PerformTransition(val, Character));
    }
    return results;
}

template<typename TState, typename TChar>
LinearSet<TState> ENFAutomaton<TState, TChar>::PerformExtendedTransition(TState State, stdx::ArraySlice<TChar> Characters) const
{
    auto states = this->Eclose(State);
    for (auto& item : Characters)
    {
        Optional<TChar> optItem(item);
        states = this->Eclose(this->PerformAllTransitions(states, optItem));
    }
    return states;
}

template<typename TState, typename TChar>
LinearSet<TState> ENFAutomaton<TState, TChar>::PerformTransition(TState State, Optional<TChar> Character) const
{
    auto transFun = this->getTransitionFunction();
    return transFun.Apply(std::pair<TState, Optional<TChar>>(State, Character));
}


/// \brief Performs the modified subset construction on this automaton.
template<typename TState, typename TChar>
DFAutomaton<LinearSet<TState>, TChar> ENFAutomaton<TState, TChar>::ToDFAutomaton() const
{
    return this->ToDFAutomaton(this->GetAlphabet());
}

/// \brief Performs the modified subset construction based on the given alphabet.
template<typename TState, typename TChar>
DFAutomaton<LinearSet<TState>, TChar> ENFAutomaton<TState, TChar>::ToDFAutomaton(LinearSet<TChar> Alphabet) const
{
    auto startState = this->Eclose(this->getStartState());
    std::unordered_map<std::pair<LinearSet<TState>, TChar>, LinearSet<TState>> transMap;
    LinearSet<LinearSet<TState>> accStates;
    LinearSet<LinearSet<TState>> processedStates;
    LinearSet<LinearSet<TState>> nextStates;
    nextStates.Add(startState);
    while (!nextStates.getIsEmpty())
    {
        auto last = nextStates.getLast();
        LinearSet<LinearSet<TState>> accumulatedStates;
        if (!processedStates.Contains(last))
        {
            for (auto& item : Alphabet.getItems())
            {
                auto trans = this->Eclose(this->PerformAllTransitions(last, Optional<TChar>(item)));
                accumulatedStates.Add(trans);
                transMap[std::pair<LinearSet<TState>, TChar>(last, item)] = trans;
            }
            processedStates.Add(last);
            if (this->ContainsAcceptingState(last))
            {
                accStates.Add(last);
            }
        }
        nextStates.RemoveLast();
        nextStates.AddAll(accumulatedStates);
    }
    TransitionTable<std::pair<LinearSet<TState>, TChar>, LinearSet<TState>> transFun(transMap);
    return DFAutomaton<LinearSet<TState>, TChar>(startState, accStates, transFun);
}

template<typename TState, typename TChar>
LinearSet<TState> ENFAutomaton<TState, TChar>::getAcceptingStates() const
{
    return this->AcceptingStates_value;
}

template<typename TState, typename TChar>
void ENFAutomaton<TState, TChar>::setAcceptingStates(LinearSet<TState> value)
{
    this->AcceptingStates_value = value;
}

template<typename TState, typename TChar>
TState ENFAutomaton<TState, TChar>::getStartState() const
{
    return this->StartState_value;
}

template<typename TState, typename TChar>
void ENFAutomaton<TState, TChar>::setStartState(TState value)
{
    this->StartState_value = value;
}

template<typename TState, typename TChar>
TransitionTable<std::pair<TState, Optional<TChar>>, LinearSet<TState>> ENFAutomaton<TState, TChar>::getTransitionFunction() const
{
    return this->TransitionFunction_value;
}

template<typename TState, typename TChar>
void ENFAutomaton<TState, TChar>::setTransitionFunction(TransitionTable<std::pair<TState, Optional<TChar>>, LinearSet<TState>> value)
{
    this->TransitionFunction_value = value;
}