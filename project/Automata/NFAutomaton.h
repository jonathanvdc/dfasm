#pragma once
#include <utility>
#include "ArraySlice.h"
#include "DFAutomaton.h"
#include "IAutomaton.h"
#include "LinearSet.h"
#include "TransitionTable.h"

namespace Automata
{
    /// \brief Defines a non-deterministic finite automaton.
    template<typename TState, typename TChar>
    class NFAutomaton : public virtual IAutomaton<TChar>
    {
    public:
        NFAutomaton(TState StartState, LinearSet<TState> AcceptingStates, TransitionTable<std::pair<TState, TChar>, LinearSet<TState>> TransitionFunction);

        /// \brief Gets a boolean value that indicates whether the automaton accepts the given string.
        bool Accepts(stdx::ArraySlice<TChar> Characters) const override;

        bool ContainsAcceptingState(LinearSet<TState> States) const;

        LinearSet<TState> getAcceptingStates() const;

        LinearSet<TChar> GetAlphabet() const;

        TState getStartState() const;

        LinearSet<TState> GetStates() const;

        TransitionTable<std::pair<TState, TChar>, LinearSet<TState>> getTransitionFunction() const;

        LinearSet<TState> PerformAllTransitions(LinearSet<TState> States, TChar Character) const;

        LinearSet<TState> PerformExtendedTransition(TState State, stdx::ArraySlice<TChar> Characters) const;

        LinearSet<TState> PerformTransition(TState State, TChar Character) const;

        /// \brief Performs the subset construction on this automaton.
        DFAutomaton<LinearSet<TState>, TChar> ToDFAutomaton() const;
    private:
        void setAcceptingStates(LinearSet<TState> value);

        void setStartState(TState value);

        void setTransitionFunction(TransitionTable<std::pair<TState, TChar>, LinearSet<TState>> value);

        /// \brief Performs the subset construction based on the given alphabet.
        DFAutomaton<LinearSet<TState>, TChar> ToDFAutomaton(LinearSet<TChar> Alphabet) const;

        LinearSet<TState> AcceptingStates_value;
        TState StartState_value;
        TransitionTable<std::pair<TState, TChar>, LinearSet<TState>> TransitionFunction_value;
    };
}

#include "NFAutomaton.hxx"