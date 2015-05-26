entry_point:
    mov eax, entry_point ; This small program returns the location
                         ; of its entry point, which varies in jit mode.
    ret
