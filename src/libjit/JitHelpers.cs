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
        public static Type CreateDelegateType(Type returnType, params Type[] parameterTypes)
        {
            // Borrowed from http://blog.bittercoder.com/2006/10/01/the-final-solution-for-generic-ironpython-delegates/

            AssemblyName assembly = new AssemblyName();
            assembly.Name = "DelegateAssembly";

            AssemblyBuilder assemblyBuilder =
                AppDomain.CurrentDomain.DefineDynamicAssembly(assembly, AssemblyBuilderAccess.Run);

            ModuleBuilder moduleBuilder = assemblyBuilder.DefineDynamicModule("TempModule");

            TypeBuilder typeBuilder =
                moduleBuilder.DefineType("TempDelegateType",
                    TypeAttributes.Public | TypeAttributes.Sealed | TypeAttributes.Class |
                    TypeAttributes.AnsiClass | TypeAttributes.AutoClass, typeof(MulticastDelegate));

            ConstructorBuilder constructorBuilder = typeBuilder.DefineConstructor(MethodAttributes.RTSpecialName | MethodAttributes.HideBySig | MethodAttributes.Public,
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
