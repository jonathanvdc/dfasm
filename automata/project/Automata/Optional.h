#pragma once

template<typename T>
struct Optional
{
    Optional();
    Optional(T Value);

    bool operator==(Optional<T> Other) const;

    bool operator==(T Other) const;

    bool operator!=(Optional<T> Other) const;

    bool operator!=(T Other) const;

    bool HasValue = false;
    T Value;
};

#include "Optional.hxx"