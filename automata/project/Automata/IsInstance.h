#pragma once
#include <memory>

namespace stdx
{
    template<typename TTarget, typename TSource>
    inline bool isinstance(const TSource* Pointer)
    {
        return dynamic_cast<const TTarget*>(Pointer) != nullptr;
    }

    template<typename TTarget, typename TSource>
    inline bool isinstance(const TSource& Reference)
    {
        return isinstance<TTarget, TSource>(&Reference);
    }

    template<typename TTarget, typename TSource>
    inline bool isinstance(std::shared_ptr<TSource> const& Pointer)
    {
        return std::dynamic_pointer_cast<TTarget, TSource>(Pointer) != nullptr;
    }
}