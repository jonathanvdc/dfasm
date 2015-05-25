.global main
.extern printf
.extern ExitProcess

main:
    xor  edx, edx       ; print "0, "
    call printInt
    call printDelimiter

    mov  edx, 1         ; print "1"
    call printInt

    xor  eax, eax       ; eax = penultimate Fibonacci number, so eax = 0 now
    mov  edx, 1         ; edx = ultimate Fibonacci number, so edx = 1 now

loop:
    push edx            ; Keep edx, eax safe on the stack
    push eax

    call printDelimiter ; Prints a delimiter (", ")

    pop  eax            ; Restore eax, edx
    pop  edx

    push edx
    add  edx, eax       ; Compute next Fibonacci number
    push edx            ; Keep edx, eax safe on the stack

    call printInt       ; print a Fibonacci number

    pop  edx            ; Restore & swap edx, eax
    pop  eax

    cmp  edx, 1836311903
    jl   loop

    mov  ecx, 0         ; Kill our process now, and report success.
    call ExitProcess
    ret                 ; Return, even though we don't *really* have to.

printInt:               ; Prints the integer in edx
    mov  ecx, msg       ; Windows x64 calling convention dictates that the first argument is passed
    jmp  callprintf     ; through ecx.

printDelimiter:         ; Prints a delimiter (", ")
    mov  ecx, delim
    jmp  callprintf

callprintf:             ; Calls printf
    xor  eax, eax       ; printf has varargs. Does eax still contain the number of stack varargs in the
                        ; Windows x64 calling convention?

    sub  esp, 32        ; Allocate 32 bytes of shadow space for printf

    call printf         ; Call printf

    add  esp, 32        ; Deallocate shadow space for printf
    ret                 ; Return

msg: .byte "%d", 0
delim: .byte ", ", 0
