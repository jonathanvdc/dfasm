.global main        ; Our main interpreter function
.extern printf      ; Define some IO functions
.extern ExitProcess

; interpretC.asm: a simple C interpreter in x64 assembly, Windows calling convention.

main:
    ; Windows x64 calling convention dictates that the first argument is passed
    ; through ecx.
    mov ecx, msg

    ; printf has varargs. Does eax still contain the number of stack varargs in the
    ; Windows x64 calling convention?
    mov eax, 0

    ; Allocate 32 bytes of shadow space for printf
    sub esp, 32

    ; Print the program's result
    call printf

    ; Deallocate shadow space for printf
    add esp, 32

    ; Everything went fine. C programs never, ever crash. Just return 0.
    mov ecx, 0
    call ExitProcess

    ret

msg:
    .byte 83, 101, 103, 109, 101, 110, 116, 97, 116, 105, 111, 110, 32, 102, 97, 117, 108, 116
    .byte 10
    .byte 0
