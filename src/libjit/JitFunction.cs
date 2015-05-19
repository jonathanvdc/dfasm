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
        }

        public VirtualBuffer Buffer { get; private set; }

        public Delegate ToDelegate(Type DelegateType)
        {
            return Marshal.GetDelegateForFunctionPointer(Buffer.Pointer, DelegateType);
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

        public static JitFunction Create(IEnumerable<byte> Data)
        {
            return new JitFunction(VirtualBuffer.Create(Data));
        }
    }
}
