﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Automata;

namespace CompileRegexCs
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var handle = Automata.Interop.Instance.CompileRegex("c*\n").Optimize();
            Console.WriteLine(handle.GetInitialState().AddInput("ccc").Accepts());
        }
    }
}
