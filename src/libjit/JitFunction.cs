using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace libjit
{
    /// <summary>
    /// Represents an native function created at runtime, 
    /// backed by a virtual buffer.
    /// </summary>
    public class JitFunction : IDisposable
    {
        /// <summary>
        /// Creates a native function with relative entry point zero
        /// backed by the given virtual buffer.
        /// </summary>
        /// <param name="Buffer"></param>
        public JitFunction(VirtualBuffer Buffer)
        {
            this.Buffer = Buffer;
            this.EntryPointOffset = 0;
        }
        /// <summary>
        /// Creates a native function backed by the given virtual buffer,
        /// and assigns it the given absolute entry point pointer.
        /// </summary>
        /// <param name="Buffer"></param>
        /// <param name="EntryPoint"></param>
        public JitFunction(VirtualBuffer Buffer, IntPtr EntryPoint)
        {
            this.Buffer = Buffer;
            this.EntryPointOffset = (int)EntryPoint - (int)Buffer.Pointer;
        }
        /// <summary>
        /// Creates a native function backed by the given buffer, and 
        /// assigns it the given relative entry point offset.
        /// </summary>
        /// <param name="Buffer"></param>
        /// <param name="EntryPointOffset"></param>
        public JitFunction(VirtualBuffer Buffer, int EntryPointOffset)
        {
            this.Buffer = Buffer;
            this.EntryPointOffset = EntryPointOffset;
        }

        /// <summary>
        /// Gets the runtime-generated native function's backing buffer.
        /// </summary>
        public VirtualBuffer Buffer { get; private set; }
        /// <summary>
        /// Gets the runtime-generated native function's relative entry point.
        /// </summary>
        public int EntryPointOffset { get; private set; }

        /// <summary>
        /// Gets the runtime-generated native function absolute entry point.
        /// </summary>
        public IntPtr EntryPoint { get { return Buffer.Pointer + EntryPointOffset; } }

        /// <summary>
        /// Creates a delegate of the given type that points to this function.
        /// </summary>
        /// <param name="DelegateType"></param>
        /// <returns></returns>
        public Delegate ToDelegate(Type DelegateType)
        {
            return Marshal.GetDelegateForFunctionPointer(EntryPoint, DelegateType);
        }

        /// <summary>
        /// Creates a strongly-typed delegate that points to this function.
        /// </summary>
        /// <typeparam name="TDelegate"></typeparam>
        /// <returns></returns>
        public TDelegate ToDelegate<TDelegate>()
        {
            return (TDelegate)(object)ToDelegate(typeof(TDelegate));
        }

        /// <summary>
        /// Invokes the native function with the given arguments, returning a value of the given type argument.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="Arguments"></param>
        /// <returns></returns>
        public T Invoke<T>(params object[] Arguments)
        {
            var delegType = JitHelpers.CreateDelegateType(
                typeof(T), Arguments.Select(item => item.GetType()).ToArray());
            var deleg = ToDelegate(delegType);
            return (T)deleg.DynamicInvoke(Arguments);
        }

        /// <summary>
        /// Frees the runtime-generated function's memory region.
        /// </summary>
        public void Dispose()
        {
            Buffer.Dispose();
        }

        /// <summary>
        /// Creates a runtime-generated native code function from the given code. 
        /// Execution starts at the allocated region's base address, which matches
        /// the first byte in the given array.
        /// </summary>
        /// <param name="Data"></param>
        /// <returns></returns>
        public static JitFunction Create(byte[] Data)
        {
            return new JitFunction(VirtualBuffer.Create(Data));
        }
        /// <summary>
        /// Creates a runtime-generated native code function from the given code
        /// and entry point offset.
        /// </summary>
        /// <param name="Data"></param>
        /// <param name="EntryPointOffset"></param>
        /// <returns></returns>
        public static JitFunction Create(byte[] Data, int EntryPointOffset)
        {
            return new JitFunction(VirtualBuffer.Create(Data), EntryPointOffset);
        }
    }
}
