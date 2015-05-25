.global main
.extern printf
.extern ExitProcess

main:
    ; Windows x64 calling convention dictates that the first argument is passed
    ; through ecx.
    mov ecx, msg

    ; printf has varargs. Does eax still contain the number of stack varargs in the
    ; Windows x64 calling convention?
    mov eax, 0

    ; Allocate 32 bytes of shadow space for printf
    sub esp, 32

    ; printf("Hello, world!");
    call printf

    ; Deallocate shadow space for printf
    add esp, 32

    ; Kill our process by calling ExitProcess(0)
    mov ecx, 0
    call ExitProcess

    ; The program should be terminated now, but we'll just 'ret' anyway, because
    ; that's what functions do. Also, we really want to make sure 'msg' is never
    ; "executed". That would be a disaster.
    ret

msg:
    .ascii "Hello, world!"
    .byte 10
    .byte 0
