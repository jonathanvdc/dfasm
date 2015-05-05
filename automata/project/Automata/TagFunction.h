#pragma once
#include <utility>
#include "IFunction.h"

namespace Automata
{
    /// \brief Defines a function that "tags" an input value with a fixed tag.
    template<typename T, typename TTag>
    struct TagFunction : public virtual IFunction<T, std::pair<T, TTag>>
    {
        /// \brief Creates a new tagging function from the given tag.
        TagFunction(TTag Tag);

        /// \brief Applies the function to the given value.
        std::pair<T, TTag> Apply(T Value) const override;

        TTag Tag;
    };
}

#include "TagFunction.hxx"