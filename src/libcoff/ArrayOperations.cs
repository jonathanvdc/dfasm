using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace libcoff
{
    public static class ArrayOperations
    {
        public static T[] Slice<T>(T[] array, int index, int length)
        {
            if (index < 0 || index > array.Length)
                throw new ArgumentOutOfRangeException("index");

            if (length < 0 || index + length > array.Length)
                throw new ArgumentOutOfRangeException("length");

            var ret = new T[length];
            Array.Copy(array, index, ret, 0, length);
            return ret;
        }

        public static T[] Resize<T>(T[] array, int newSize)
        {
            var newArray = new T[newSize];
            var minLength = Math.Min(newSize, array.Length);

            Array.Copy(array, newArray, minLength);

            return newArray;
        }

        public static T[] Concat<T>(T[] array, T value)
        {
            var ret = new T[array.Length + 1];
            ret[array.Length] = value;
            return ret;
        }

        public static int IndexOf<T>(this IReadOnlyList<T> Values, T Value)
        {
            for (int i = 0; i < Values.Count; i++)
            {
                if (object.Equals(Values[i], Value))
                {
                    return i;
                }
            }
            return -1;
        }
    }
}
