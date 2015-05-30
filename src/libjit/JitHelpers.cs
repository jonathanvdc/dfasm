using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;
using System.Threading.Tasks;

namespace libjit
{
    public static class JitHelpers
    {
        /// <summary>
        /// Creates a delegate type from the given return type and parameter types.
        /// This delegate type can then be used to create a delegate for a JIT function
        /// at runtime, invoking it based on the types of the arguments that were passed
        /// to the function.
        /// </summary>
        /// <param name="returnType"></param>
        /// <param name="parameterTypes"></param>
        /// <returns></returns>
        public static Type CreateDelegateType(Type returnType, params Type[] parameterTypes)
        {
            // Borrowed from:
            // http://blog.bittercoder.com/2006/10/01/the-final-solution-for-generic-ironpython-delegates/

            AssemblyName assembly = new AssemblyName();
            assembly.Name = "DelegateAssembly";

            AssemblyBuilder assemblyBuilder =
                AppDomain.CurrentDomain.DefineDynamicAssembly(assembly, AssemblyBuilderAccess.Run);

            ModuleBuilder moduleBuilder = assemblyBuilder.DefineDynamicModule("TempModule");

            TypeBuilder typeBuilder =
                moduleBuilder.DefineType("TempDelegateType",
                    TypeAttributes.Public | TypeAttributes.Sealed | TypeAttributes.Class |
                    TypeAttributes.AnsiClass | TypeAttributes.AutoClass, typeof(MulticastDelegate));

            ConstructorBuilder constructorBuilder = typeBuilder.DefineConstructor(
                MethodAttributes.RTSpecialName | MethodAttributes.HideBySig | MethodAttributes.Public,
                 CallingConventions.Standard, new Type[] { typeof(object), typeof(int) });
            constructorBuilder.SetImplementationFlags(MethodImplAttributes.Runtime | MethodImplAttributes.Managed);

            MethodBuilder methodBuilder =
                typeBuilder.DefineMethod("Invoke",
                    MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.NewSlot |
                    MethodAttributes.Virtual, returnType, parameterTypes);

            methodBuilder.SetImplementationFlags(MethodImplAttributes.Managed | MethodImplAttributes.Runtime);

            return typeBuilder.CreateType();
        }
    }
}
