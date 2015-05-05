#pragma once
#include "IFunction.h"

namespace Automata
{
    /// \brief Defines an "id" function.
    template<typename T>
    struct IdFunction : public virtual IFunction<T, T>
    {
        /// \brief Creates a new "id" function.
        IdFunction();

        /// \brief Applies the function to the given value.
        T Apply(T Value) const override;
    };
}

#include "IdFunction.hxx"