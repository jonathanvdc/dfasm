#pragma once
#include "ArraySlice.h"

namespace Automata
{
    /// \brief Defines common automaton functionality.
    template<typename TChar>
    struct IAutomaton
    {
        /// \brief Gets a boolean value that indicates whether the automaton accepts the given string.
        virtual bool Accepts(stdx::ArraySlice<TChar> Characters) const = 0;
    };
}