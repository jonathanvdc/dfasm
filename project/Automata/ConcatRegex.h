#pragma once
#include <memory>
#include <string>
#include "ENFAutomaton.h"
#include "IRegex.h"
#include "RegexState.h"

namespace Automata
{
    struct ConcatRegex : public virtual IRegex
    {
        ConcatRegex(std::shared_ptr<IRegex> Left, std::shared_ptr<IRegex> Right);

        ENFAutomaton<std::shared_ptr<RegexState>, std::string> ToENFAutomaton() const override;

        std::string ToString() const override;

        std::shared_ptr<IRegex> Left;
        std::shared_ptr<IRegex> Right;
    };
}