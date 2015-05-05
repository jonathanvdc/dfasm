#pragma once
#include <utility>
#include "ArraySlice.h"
#include "DFAutomaton.h"
#include "IAutomaton.h"
#include "IFunction.h"
#include "LinearSet.h"
#include "Optional.h"
#include "TransitionTable.h"

namespace Automata
{
    /// \brief Defines a non-deterministic finite automaton with epsilon transitions.
    template<typename TState, typename TChar>
    class ENFAutomaton : public virtual IAutomaton<TChar>
    {
    public:
        ENFAutomaton(TState StartState, LinearSet<TState> AcceptingStates, TransitionTable<std::pair<TState, Optional<TChar>>, LinearSet<TState>> TransitionFunction);

        /// \brief Gets a boolean value that indicates whether the automaton accepts the given string.
        bool Accepts(stdx::ArraySlice<TChar> Characters) const override;

        bool ContainsAcceptingState(LinearSet<TState> States) const;

        LinearSet<TState> Eclose(TState State) const;

        LinearSet<TState> Eclose(LinearSet<TState> States) const;

        LinearSet<TState> getAcceptingStates() const;

        LinearSet<TChar> GetAlphabet() const;

        TState getStartState() const;

        LinearSet<TState> GetStates() const;

        TransitionTable<std::pair<TState, Optional<TChar>>, LinearSet<TState>> getTransitionFunction() const;

        LinearSet<TState> PerformAllTransitions(LinearSet<TState> States, Optional<TChar> Character) const;

        LinearSet<TState> PerformExtendedTransition(TState State, stdx::ArraySlice<TChar> Characters) const;

        LinearSet<TState> PerformTransition(TState State, Optional<TChar> Character) const;

        template<typename TNState, typename TNChar>
        ENFAutomaton<TNState, TNChar> Rename(const IFunction<TState, TNState>* StateRenamer, const IFunction<TChar, TNChar>* CharRenamer) const
        {
            auto newStart = StateRenamer->Apply(this->getStartState());
            LinearSet<TNState> newAccept;
            auto oldAccept = this->getAcceptingStates();
            for (auto& val : oldAccept.getItems())
            {
                newAccept.Add(StateRenamer->Apply(val));
            }
            auto currentTransFun = this->getTransitionFunction();
            std::unordered_map<std::pair<TNState, Optional<TNChar>>, LinearSet<TNState>> newTransMap;
            for (auto& item : currentTransFun.getMap())
            {
                auto renamedOriginState = StateRenamer->Apply(item.first.first);
                LinearSet<TNState> renamedTargetStates;
                for (auto& state : item.second.getItems())
                {
                    renamedTargetStates.Add(StateRenamer->Apply(state));
                }
                if (item.first.second.HasValue)
                {
                    newTransMap[std::pair<TNState, Optional<TNChar>>(renamedOriginState, Optional<TNChar>(CharRenamer->Apply(item.first.second.Value)))] = renamedTargetStates;
                }
                else
                {
                    newTransMap[std::pair<TNState, Optional<TNChar>>(renamedOriginState, Optional<TNChar>())] = renamedTargetStates;
                }
            }
            TransitionTable<std::pair<TNState, Optional<TNChar>>, LinearSet<TNState>> transFun(newTransMap);
            return ENFAutomaton<TNState, TNChar>(newStart, newAccept, transFun);
        }

        /// \brief Performs the modified subset construction on this automaton.
        DFAutomaton<LinearSet<TState>, TChar> ToDFAutomaton() const;
    private:
        void setAcceptingStates(LinearSet<TState> value);

        void setStartState(TState value);

        void setTransitionFunction(TransitionTable<std::pair<TState, Optional<TChar>>, LinearSet<TState>> value);

        /// \brief Performs the modified subset construction based on the given alphabet.
        DFAutomaton<LinearSet<TState>, TChar> ToDFAutomaton(LinearSet<TChar> Alphabet) const;

        LinearSet<TState> AcceptingStates_value;
        TState StartState_value;
        TransitionTable<std::pair<TState, Optional<TChar>>, LinearSet<TState>> TransitionFunction_value;
    };
}

#include "ENFAutomaton.hxx"