
    ; Calculates the nth Fibonacci number (n > 0).
    ; Signature: stdcall int(int)
    ; Usage: ipy dfasm.py -jit -arg:12 -ret:int < jitfib.asm

    mov  ebx, esp
    mov  ecx, [ebx + 4] ; Load n into ecx
    mov  eax, 0         ; Setup eax, ebx
    mov  ebx, 1
fib:
    add  eax, ebx       ; Compute next Fibonacci number
    xchg ebx, eax       ; Swap eax, ebx

    dec ecx             ; Decrement counter

    cmp  ecx, 0         ; Check if we're not done yet
    jg   fib

    ret                 ; Return eax
