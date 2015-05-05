#pragma once

namespace Automata
{
    /// \brief Defines common functionality for a generic pure function.
    template<typename TSource, typename TTarget>
    struct IFunction
    {
        /// \brief Applies the function to the given value.
        virtual TTarget Apply(TSource Value) const = 0;
    };
}