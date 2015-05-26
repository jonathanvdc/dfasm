using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace libjit
{
    public class JitFunction : IDisposable
    {
        public JitFunction(VirtualBuffer Buffer)
        {
            this.Buffer = Buffer;
            this.EntryPointOffset = 0;
        }
        public JitFunction(VirtualBuffer Buffer, IntPtr EntryPoint)
        {
            this.Buffer = Buffer;
            this.EntryPointOffset = (int)EntryPoint - (int)Buffer.Pointer;
        }
        public JitFunction(VirtualBuffer Buffer, int EntryPointOffset)
        {
            this.Buffer = Buffer;
            this.EntryPointOffset = EntryPointOffset;
        }

        public VirtualBuffer Buffer { get; private set; }
        public int EntryPointOffset { get; private set; }

        public IntPtr EntryPoint { get { return Buffer.Pointer + EntryPointOffset; } }

        public Delegate ToDelegate(Type DelegateType)
        {
            return Marshal.GetDelegateForFunctionPointer(EntryPoint, DelegateType);
        }

        public TDelegate ToDelegate<TDelegate>()
        {
            return (TDelegate)(object)ToDelegate(typeof(TDelegate));
        }

        public T Invoke<T>(params object[] Arguments)
        {
            var delegType = JitHelpers.CreateDelegateType(typeof(T), Arguments.Select(item => item.GetType()).ToArray());
            var deleg = ToDelegate(delegType);
            return (T)deleg.DynamicInvoke(Arguments);
        }

        public void Dispose()
        {
            Buffer.Dispose();
        }

        public static JitFunction Create(byte[] Data)
        {
            return new JitFunction(VirtualBuffer.Create(Data));
        }
        public static JitFunction Create(byte[] Data, int EntryPointOffset)
        {
            return new JitFunction(VirtualBuffer.Create(Data), EntryPointOffset);
        }
    }
}
