#include "Optional.h"


template<typename T>
Optional<T>::Optional()
{
    this->HasValue = false;
}

template<typename T>
Optional<T>::Optional(T Value)
{
    this->Value = Value;
    this->HasValue = true;
}

template<typename T>
bool Optional<T>::operator==(Optional<T> Other) const
{
    if (this->HasValue)
        return Other.HasValue && this->Value == Other.Value;
    else
        return !Other.HasValue;

}

template<typename T>
bool Optional<T>::operator==(T Other) const
{
    return this->HasValue && this->Value == Other;
}

template<typename T>
bool Optional<T>::operator!=(Optional<T> Other) const
{
    if (!this->HasValue)
        return Other.HasValue;
    else
        return !Other.HasValue || this->Value != Other.Value;

}

template<typename T>
bool Optional<T>::operator!=(T Other) const
{
    return !this->HasValue || this->Value == Other;
}