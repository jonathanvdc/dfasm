.global main
    mov eax, 2
    ret
main:
    mov eax, main ; This small program returns the location
                  ; of its entry point, which varies in jit mode.
    ret
