#pragma once
#include "RegexState.h"
#include "IRegex.h"
#include "PhiRegex.h"
#include "LiteralRegex.h"
#include "EpsilonRegex.h"
#include "UnionRegex.h"
#include "ConcatRegex.h"
#include "ClosureRegex.h"
#include "HashExtensions.h"

class RegexParser
{
public:
	RegexParser(std::istream& Input) : data(&Input) { }

	std::shared_ptr<IRegex> ParseRegex();

private:
	std::istream* data;
	std::shared_ptr<IRegex> ParseSimpleRegex(char Value);
	std::shared_ptr<IRegex> ParsePrimaryRegex(char Value);
	std::shared_ptr<IRegex> ParseRegex(char Value);
};