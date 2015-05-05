#pragma once
#include <utility>
#include "LinearSet.h"
#include "Optional.h"
#include "RegexState.h"

namespace std
{
	template<typename T, typename V>
	struct hash<std::pair<T, V>>
	{
		size_t operator() (const std::pair<T, V>& Value) const
		{
			return hash<T>()(Value.first) ^ hash<V>()(Value.second);
		}
	};

	template<typename T>
	struct hash<LinearSet<T>>
	{
		size_t operator()(const LinearSet<T>& Value) const
		{
			size_t result = 0;
			for (auto item : Value.getItems())
			{
				result ^= hash<T>()(item);
			}
			return result;
		}
	};

	template<typename T>
	struct hash<Optional<T>>
	{
		size_t operator()(const Optional<T>& Value) const
		{
			if (!Value.HasValue) return 0;
			else return hash<T>()(Value.Value);
		}
	};

	template<>
	struct hash<std::shared_ptr<RegexState>>
	{
		size_t operator()(const std::shared_ptr<RegexState>& Value) const
		{
			return (size_t)Value.get();
		}
	};
}
