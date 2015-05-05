#include "IdFunction.h"

#include "IFunction.h"

using namespace Automata;

/// \brief Creates a new "id" function.
template<typename T>
IdFunction<T>::IdFunction()
{ }

/// \brief Applies the function to the given value.
template<typename T>
T IdFunction<T>::Apply(T Value) const
{
    return Value;
}