#pragma once
#include <memory>
#include <string>
#include "ENFAutomaton.h"
#include "IRegex.h"
#include "RegexState.h"

namespace Automata
{
    struct LiteralRegex : public virtual IRegex
    {
        LiteralRegex(std::string Literal);

        ENFAutomaton<std::shared_ptr<RegexState>, std::string> ToENFAutomaton() const override;

        std::string ToString() const override;

        std::string Literal;
    };
}