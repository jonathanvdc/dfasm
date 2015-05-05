#include "ArraySlice.h"

#include <initializer_list>
#include <memory>
#include <vector>

using namespace stdx;

template<typename T>
ArraySlice<T>::ArraySlice()
    : ptr(std::make_shared<std::vector<T>>()), length(0), offset(0)
{
}

template<typename T>
ArraySlice<T>::ArraySlice(typename ArraySlice<T>::size_type Length)
    : ptr(std::make_shared<std::vector<T>>(Length)), length(Length), offset(0)
{
}

template<typename T>
ArraySlice<T>::ArraySlice(std::shared_ptr<std::vector<T>> Array, typename ArraySlice<T>::size_type Length)
    : ptr(Array), length(Length), offset(0)
{
}

template<typename T>
ArraySlice<T>::ArraySlice(std::initializer_list<T> Values)
    : ptr(std::make_shared<std::vector<T>>(Values)), offset(0)
{
    this->length = this->ptr->size();
}

template<typename T>
ArraySlice<T>::ArraySlice(T* Array, typename ArraySlice<T>::size_type Length)
    : ptr(std::make_shared<std::vector<T>>(Length)), length(Length), offset(0)
{
    for (typename ArraySlice<T>::size_type i = 0; i < Length; i++)
    {
        (*this)[i] = Array[i];
    }
}

template<typename T>
ArraySlice<T>::ArraySlice(std::shared_ptr<std::vector<T>> Array, typename ArraySlice<T>::size_type Offset, typename ArraySlice<T>::size_type Length)
    : ptr(Array), length(Length), offset(Offset)
{
}

template<typename T>
ArraySlice<T>::ArraySlice(const ArraySlice<T>& Other)
    : ptr(Other.ptr), length(Other.length), offset(Other.offset)
{
}

template<typename T>
ArraySlice<T>::ArraySlice(const std::vector<T>& Values)
    : ptr(std::make_shared<std::vector<T>>(Values)), length(Values.size()), offset(0)
{
}

template<typename T>
T& ArraySlice<T>::operator[](typename ArraySlice<T>::size_type Index)
{
    return this->ptr->at(this->offset + Index);
}

template<typename T>
const T& ArraySlice<T>::operator[](typename ArraySlice<T>::size_type Index) const
{
    return this->ptr->at(this->offset + Index);
}

template<typename T>
ArraySlice<T>& ArraySlice<T>::operator=(const ArraySlice<T>& Other)
{
    this->ptr = Other.ptr;
    this->length = Other.length;
    this->offset = Other.offset;
    return *this;
}

template<typename T>
ArraySlice<T>::operator std::vector<T>() const
{
    if (offset == 0 && this->GetLength() == ptr->size())
    {
        return *ptr; // Fast path. Just copy the vector.
    }
    else
    {
        std::vector<T> vals(this->GetLength()); // Slow path. Offset is not zero or length does not equal size. These things happen.
        for (typename ArraySlice<T>::size_type i = 0; i < this->GetLength(); i++)
        {
            vals[i] = (*this)[i];
        }
        return vals;
    }
}

template<typename T>
ArraySlice<T> ArraySlice<T>::Slice(typename ArraySlice<T>::size_type Start, typename ArraySlice<T>::size_type Length) const
{
    return ArraySlice<T>(this->ptr, Start + this->offset, Length);
}

template<typename T>
ArraySlice<T> ArraySlice<T>::Slice(typename ArraySlice<T>::size_type Start) const
{
    return Slice(Start, this->length - Start);
}

template<typename T>
typename ArraySlice<T>::size_type ArraySlice<T>::GetLength() const
{
    return this->length;
}

template<typename T>
typename ArraySlice<T>::iterator ArraySlice<T>::begin()
{
    return ArraySlice<T>::iterator(this->ptr, this->offset);
}

template<typename T>
typename ArraySlice<T>::iterator ArraySlice<T>::end()
{
    return ArraySlice<T>::iterator(this->ptr, this->offset + this->length);
}

template<typename T>
typename ArraySlice<T>::const_iterator ArraySlice<T>::begin() const
{
    return this->cbegin();
}

template<typename T>
typename ArraySlice<T>::const_iterator ArraySlice<T>::end() const
{
    return this->cend();
}

template<typename T>
typename ArraySlice<T>::const_iterator ArraySlice<T>::cbegin() const
{
    return ArraySlice<T>::const_iterator(this->ptr, this->offset);
}

template<typename T>
typename ArraySlice<T>::const_iterator ArraySlice<T>::cend() const
{
    return ArraySlice<T>::const_iterator(this->ptr, this->offset + this->length);
}