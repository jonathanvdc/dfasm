#pragma once
#include <initializer_list>
#include <memory>
#include <vector>

namespace stdx
{
    template<typename T>
    class ArraySlice
    {
    public:
        typedef int size_type;
        typedef int offset_type;
        typedef int difference_type;

        ArraySlice();
        ArraySlice(size_type Length);
        ArraySlice(std::shared_ptr<std::vector<T>> Array, size_type Length);
        ArraySlice(std::initializer_list<T> Values);
        ArraySlice(const std::vector<T>& Values);
        ArraySlice(T* Array, size_type Length);
        ArraySlice(const ArraySlice<T>& Other);

        T& operator[](size_type Index);
        const T& operator[](size_type Index) const;
        ArraySlice<T>& operator=(const ArraySlice<T>& Other);
        operator std::vector<T>() const;

        ArraySlice<T> Slice(size_type Start, size_type Length) const;
        ArraySlice<T> Slice(size_type Start) const;

        size_type GetLength() const;

        class iterator
        {
        public:
            iterator(std::shared_ptr<std::vector<T>> Pointer, size_type Index) : ptr(Pointer), index(Index) { }
            T& operator*() const { return ptr->at(index); }
            T& operator[](offset_type Index) const { return ptr->at(index + Index); }
            iterator& operator++() { this->index++; return *this; }
            iterator& operator--() { this->index--; return *this; }
            iterator operator+(offset_type Offset) const { return iterator(this->ptr, index + Offset); }
            iterator operator-(offset_type Offset) const { return iterator(this->ptr, index - Offset); }
            iterator& operator+=(offset_type Offset) const { this->index += Offset; return *this; }
            iterator& operator-=(offset_type Offset) const { this->index -= Offset; return *this; }
            bool operator==(iterator& Other) const { return this->index == Other.index; }
            bool operator!=(iterator& Other) const { return this->index != Other.index; }
            difference_type operator-(iterator& Other) const { return this->index - Other.index; }
            bool operator<(iterator& Other) const { return this->index < Other.index; }
            bool operator<=(iterator& Other) const { return this->index <= Other.index; }
            bool operator>(iterator& Other) const { return this->index > Other.index; }
            bool operator>=(iterator& Other) const { return this->index >= Other.index; }

        private:
            std::shared_ptr<std::vector<T>> ptr;
            size_type index;
        };

        class const_iterator
        {
        public:
            const_iterator(std::shared_ptr<std::vector<T>> Pointer, size_type Index) : ptr(Pointer), index(Index) { }
            const T& operator*() const { return ptr->at(index); }
            const T& operator[](offset_type Index) const { return ptr->at(index + Index); }
            const_iterator& operator++() { this->index++; return *this; }
            const_iterator& operator--() { this->index--; return *this; }
            const_iterator operator+(offset_type Offset) const { return const_iterator(this->ptr, index + Offset); }
            const_iterator operator-(offset_type Offset) const { return const_iterator(this->ptr, index - Offset); }
            const_iterator& operator+=(offset_type Offset) const { this->index += Offset; return *this; }
            const_iterator& operator-=(offset_type Offset) const { this->index -= Offset; return *this; }
            bool operator==(const_iterator& Other) const { return this->index == Other.index; }
            bool operator!=(const_iterator& Other) const { return this->index != Other.index; }
            difference_type operator-(const_iterator& Other) const { return this->index - Other.index; }
            bool operator<(const_iterator& Other) const { return this->index < Other.index; }
            bool operator<=(const_iterator& Other) const { return this->index <= Other.index; }
            bool operator>(const_iterator& Other) const { return this->index > Other.index; }
            bool operator>=(const_iterator& Other) const { return this->index >= Other.index; }

        private:
            std::shared_ptr<std::vector<T>> ptr;
            size_type index;
        };

        iterator begin();
        iterator end();
        const_iterator begin() const;
        const_iterator end() const;
        const_iterator cbegin() const;
        const_iterator cend() const;

    private:

        ArraySlice(std::shared_ptr<std::vector<T>> Array, size_type Offset, size_type Length);

        std::shared_ptr<std::vector<T>> ptr;
        size_type offset, length;
    };
}

#include "ArraySlice.hxx"