#pragma once
#include <memory>
#include <string>
#include "ENFAutomaton.h"
#include "RegexState.h"

namespace Automata
{
    /// \brief Defines a generic regular expression.
    struct IRegex
    {
        virtual ENFAutomaton<std::shared_ptr<RegexState>, std::string> ToENFAutomaton() const = 0;

        virtual std::string ToString() const = 0;
    };
}