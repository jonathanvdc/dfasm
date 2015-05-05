#pragma once
#include <functional>
#include "IFunction.h"

namespace Automata
{
	template<typename TSource, typename TTarget>
	class LambdaFunction : public IFunction<TSource, TTarget>
	{
	private:
		std::function<TTarget(TSource)> func;

		TTarget Apply(TSource Value) const
		{
			return func(Value);
		}

	public:
		LambdaFunction(std::function<TTarget(TSource)> Function)
		{
			this->func = Function;
		}
	};
}