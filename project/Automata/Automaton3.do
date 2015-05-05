digraph enfa {
    rankdir = LR;
    __start [style = invis, shape = point];
    __start -> "a" [ label = "start" ];
    node [shape = doublecircle]; "c"
    node [shape = circle];
    "a" -> "a" [ label = "a" ];
    "b" -> "b" [ label = "b" ];
    "c" -> "c" [ label = "c" ];
    "a" -> "b" [ label = "epsilon" ];
    "b" -> "c" [ label = "epsilon" ];
}
