#pragma once
#include <unordered_map>
#include "IFunction.h"

namespace Automata
{
    /// \brief Defines a transition table that uses an unordered_map under the hood.
    template<typename TSource, typename TTarget>
    class TransitionTable : public virtual IFunction<TSource, TTarget>
    {
    public:
        TransitionTable();
        TransitionTable(std::unordered_map<TSource, TTarget> table);

        void Add(TransitionTable<TSource, TTarget> Transitions);

        void Add(std::unordered_map<TSource, TTarget> Transitions);

        void Add(TSource Source, TTarget Target);

        /// \brief Applies the function to the given value.
        TTarget Apply(TSource Value) const override;

        std::unordered_map<TSource, TTarget> getMap() const;
    private:
        std::unordered_map<TSource, TTarget> table;
    };
}

#include "TransitionTable.hxx"