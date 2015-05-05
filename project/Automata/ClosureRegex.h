#pragma once
#include <memory>
#include <string>
#include "ENFAutomaton.h"
#include "IRegex.h"
#include "RegexState.h"

namespace Automata
{
    struct ClosureRegex : public virtual IRegex
    {
        ClosureRegex(std::shared_ptr<IRegex> Regex);

        ENFAutomaton<std::shared_ptr<RegexState>, std::string> ToENFAutomaton() const override;

        std::string ToString() const override;

        std::shared_ptr<IRegex> Regex;
    };
}