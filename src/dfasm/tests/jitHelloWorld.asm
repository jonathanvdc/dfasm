    ; Returns "Hello, World!"
    ; Signature: stdcall char*()
    ; Usage: ipy dfasm.py -jit -ret:str < jitHelloWorld.asm

    mov eax, msg                ; Move pointer into eax
    ret                         ; Return
msg:
    .byte "Hello, World!", 0    ; "Hello, World!\0" constant
