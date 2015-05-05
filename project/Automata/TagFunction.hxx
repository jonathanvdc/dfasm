#include "TagFunction.h"

#include <utility>
#include "IFunction.h"

using namespace Automata;

/// \brief Creates a new tagging function from the given tag.
template<typename T, typename TTag>
TagFunction<T, TTag>::TagFunction(TTag Tag)
{
    this->Tag = Tag;
}

/// \brief Applies the function to the given value.
template<typename T, typename TTag>
std::pair<T, TTag> TagFunction<T, TTag>::Apply(T Value) const
{
    return std::pair<T, TTag>(Value, this->Tag);
}