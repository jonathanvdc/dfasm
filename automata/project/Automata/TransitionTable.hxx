#include "TransitionTable.h"

#include <unordered_map>
#include <utility>
#include "IFunction.h"

using namespace Automata;

template<typename TSource, typename TTarget>
TransitionTable<TSource, TTarget>::TransitionTable()
{ }

template<typename TSource, typename TTarget>
TransitionTable<TSource, TTarget>::TransitionTable(std::unordered_map<TSource, TTarget> table)
{
    this->table = table;
}

template<typename TSource, typename TTarget>
void TransitionTable<TSource, TTarget>::Add(TransitionTable<TSource, TTarget> Transitions)
{
    this->Add(Transitions.getMap());
}

template<typename TSource, typename TTarget>
void TransitionTable<TSource, TTarget>::Add(std::unordered_map<TSource, TTarget> Transitions)
{
    for (auto& item : Transitions)
        this->Add(item.first, item.second);
}

template<typename TSource, typename TTarget>
void TransitionTable<TSource, TTarget>::Add(TSource Source, TTarget Target)
{
    this->table[Source] = Target;
}

/// \brief Applies the function to the given value.
template<typename TSource, typename TTarget>
TTarget TransitionTable<TSource, TTarget>::Apply(TSource Value) const
{
    return this->getMap()[Value];
}

template<typename TSource, typename TTarget>
std::unordered_map<TSource, TTarget> TransitionTable<TSource, TTarget>::getMap() const
{
    return this->table;
}