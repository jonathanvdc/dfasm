.global main
.extern printf
.extern ExitProcess

main:
    ; eax = penultimate Fibonacci number
    ; ebx = ultimate Fibonacci number

    xor eax, eax ; print "0, "
    call printInt
    call printDelimiter

    mov eax, 1 ; print "1, "
    call printInt
    call printDelimiter

    xor eax, eax ; Setup eax, ebx
    mov ebx, 1

    jmp loopBody

loop:
    push ebx ; Keep ebx, eax safe on the stack
    push eax

    call printDelimiter ; Prints a delimiter (", ")

    pop eax ; Restore eax, ebx
    pop ebx

loopBody:
    add  eax, ebx ; Compute next Fibonacci number

    push ebx ; Keep ebx, eax safe on the stack
    push eax

    call printInt ; print a Fibonacci number

    pop ebx ; Restore & swap ebx, eax
    pop eax

    cmp ebx, 1836311903
    jl loop

    mov ecx, 0
    call ExitProcess

    ret

printInt: ; Prints a single integer
    ; Pass the integer argument through eax
    mov edx, eax

    ; Windows x64 calling convention dictates that the first argument is passed
    ; through ecx.
    mov ecx, msg

    ; printf has varargs. Does eax still contain the number of stack varargs in the
    ; Windows x64 calling convention?
    xor eax, eax

    ; Allocate 32 bytes of shadow space for printf
    sub esp, 32

    ; printf("%d");
    call printf

    ; Deallocate shadow space for printf
    add esp, 32

    ret ; Return

printDelimiter: ; Prints a delimiter
    ; Windows x64 calling convention dictates that the first argument is passed
    ; through ecx.
    mov ecx, delim

    ; printf has varargs. Does eax still contain the number of stack varargs in the
    ; Windows x64 calling convention?
    xor eax, eax

    ; Allocate 32 bytes of shadow space for printf
    sub esp, 32

    ; printf(", ");
    call printf

    ; Deallocate shadow space for printf
    add esp, 32

    ret ; Return

msg:
    .byte "%d"
    .byte 0

delim:
    .byte ", "
    .byte 0
