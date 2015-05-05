#pragma once
#include <unordered_map>
#include <utility>
#include "ArraySlice.h"
#include "IAutomaton.h"
#include "IFunction.h"
#include "LinearSet.h"
#include "TransitionTable.h"

namespace Automata
{
    /// \brief Defines a deterministic finite automaton.
    template<typename TState, typename TChar>
    class DFAutomaton : public virtual IAutomaton<TChar>
    {
    public:
        DFAutomaton(TState StartState, LinearSet<TState> AcceptingStates, TransitionTable<std::pair<TState, TChar>, TState> TransitionFunction);

        /// \brief Gets a boolean value that indicates whether the automaton accepts the given string.
        bool Accepts(stdx::ArraySlice<TChar> Characters) const override;

        bool EquivalentTo(DFAutomaton<TState, TChar> other) const;

        LinearSet<TState> getAcceptingStates() const;

        LinearSet<TChar> GetAlphabet() const;

        TState getStartState() const;

        LinearSet<TState> GetStates() const;

        TransitionTable<std::pair<TState, TChar>, TState> getTransitionFunction() const;

        bool IsAcceptingState(TState State) const;

        DFAutomaton<LinearSet<TState>, TChar> Optimize() const;

        TState PerformExtendedTransition(TState State, stdx::ArraySlice<TChar> Characters) const;

        TState PerformTransition(TState State, TChar Character) const;

        LinearSet<TState> ReachableStates() const;

        template<typename TNState, typename TNChar>
        DFAutomaton<TNState, TNChar> Rename(const IFunction<TState, TNState>* StateRenamer, const IFunction<TChar, TNChar>* CharRenamer) const
        {
            auto newStart = StateRenamer->Apply(this->getStartState());
            LinearSet<TNState> newAccept;
            auto oldAccept = this->getAcceptingStates();
            for (auto& item : oldAccept.getItems())
            {
                newAccept.Add(StateRenamer->Apply(item));
            }
            auto currentTransFun = this->getTransitionFunction();
            std::unordered_map<std::pair<TNState, TNChar>, TNState> newTransMap;
            for (auto& item0 : currentTransFun.getMap())
            {
                newTransMap[std::pair<TNState, TNChar>(StateRenamer->Apply(item0.first.first), CharRenamer->Apply(item0.first.second))] = StateRenamer->Apply(item0.second);
            }
            TransitionTable<std::pair<TNState, TNChar>, TNState> transFun(newTransMap);
            return DFAutomaton<TNState, TNChar>(newStart, newAccept, transFun);
        }

        std::unordered_map<TState, LinearSet<TState>> TFAPartition() const;
    private:
        void setAcceptingStates(LinearSet<TState> value);

        void setStartState(TState value);

        void setTransitionFunction(TransitionTable<std::pair<TState, TChar>, TState> value);

        LinearSet<TState> AcceptingStates_value;
        TState StartState_value;
        TransitionTable<std::pair<TState, TChar>, TState> TransitionFunction_value;
    };
}

#include "DFAutomaton.hxx"