#pragma once
#include <initializer_list>
#include <vector>
#include "ArraySlice.h"

template<typename T>
class LinearSet
{
public:
    LinearSet();
    LinearSet(std::vector<T> Values);
    LinearSet(stdx::ArraySlice<T> Values);
    LinearSet(std::initializer_list<T> Values);
    LinearSet(T Value);

    void Add(T Value);

    void AddAll(LinearSet<T> Other);

    bool Contains(T Value) const;

    bool ContainsAll(LinearSet<T> Values) const;

    LinearSet<T> Intersect(LinearSet<T> Other) const;

    /// \brief Removes the last element from the linear set and returns it.
    T Pop();

    void RemoveLast();

    LinearSet<T> Union(LinearSet<T> Other) const;

    LinearSet<T> Without(T Value) const;

    int getCount() const;

    bool getIsEmpty() const;

    std::vector<T> getItems() const;

    T getLast() const;

    bool operator==(LinearSet<T> Other) const;

    bool operator!=(LinearSet<T> Other) const;
private:
    std::vector<T> vals;
};

#include "LinearSet.hxx"