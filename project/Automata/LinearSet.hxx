#include "LinearSet.h"

#include <initializer_list>
#include <vector>
#include "ArraySlice.h"

template<typename T>
LinearSet<T>::LinearSet()
{ }

template<typename T>
LinearSet<T>::LinearSet(std::vector<T> Values)
{
    this->vals = Values;
}

template<typename T>
LinearSet<T>::LinearSet(stdx::ArraySlice<T> Values)
{
    this->vals = (std::vector<T>)Values;
}

template<typename T>
LinearSet<T>::LinearSet(std::initializer_list<T> Values)
{
    this->vals = std::vector<T>(Values);
}

template<typename T>
LinearSet<T>::LinearSet(T Value)
{
    this->vals.push_back(Value);
}

template<typename T>
void LinearSet<T>::Add(T Value)
{
    if (!this->Contains(Value))
        this->vals.push_back(Value);

}

template<typename T>
void LinearSet<T>::AddAll(LinearSet<T> Other)
{
    for (auto& item : Other.vals)
        this->Add(item);
}

template<typename T>
bool LinearSet<T>::Contains(T Value) const
{
    for (auto& item : this->vals)
        if (item == Value)
            return true;

    return false;
}

template<typename T>
bool LinearSet<T>::ContainsAll(LinearSet<T> Values) const
{
    for (auto& item : Values.vals)
        if (!this->Contains(item))
            return false;

    return true;
}

template<typename T>
LinearSet<T> LinearSet<T>::Intersect(LinearSet<T> Other) const
{
    LinearSet<T> result;
    for (auto& item : this->vals)
    {
        if (Other.Contains(item))
        {
            result.Add(item);
        }
    }
    return result;
}

/// \brief Removes the last element from the linear set and returns it.
template<typename T>
T LinearSet<T>::Pop()
{
    auto elem = this->getLast();
    this->RemoveLast();
    return elem;
}

template<typename T>
void LinearSet<T>::RemoveLast()
{
    this->vals.pop_back();
}

template<typename T>
LinearSet<T> LinearSet<T>::Union(LinearSet<T> Other) const
{
    auto copy = *this;
    copy.AddAll(Other);
    return copy;
}

template<typename T>
LinearSet<T> LinearSet<T>::Without(T Value) const
{
    LinearSet<T> result;
    for (auto& item : this->getItems())
    {
        if (item != Value)
        {
            result.Add(item);
        }
    }
    return result;
}

template<typename T>
int LinearSet<T>::getCount() const
{
    return (int)this->vals.size();
}

template<typename T>
bool LinearSet<T>::getIsEmpty() const
{
    return this->getCount() == 0;
}

template<typename T>
std::vector<T> LinearSet<T>::getItems() const
{
    return this->vals;
}

template<typename T>
T LinearSet<T>::getLast() const
{
    return this->vals[this->getCount() - 1];
}

template<typename T>
bool LinearSet<T>::operator==(LinearSet<T> Other) const
{
    return this->ContainsAll(Other) && Other.ContainsAll(*this);
}

template<typename T>
bool LinearSet<T>::operator!=(LinearSet<T> Other) const
{
    return !this->ContainsAll(Other) || !Other.ContainsAll(*this);
}