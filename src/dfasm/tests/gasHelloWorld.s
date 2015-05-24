.text
.globl main
main:
    mov $msg, %ecx
    call printf

    mov $0, %ecx
    call ExitProcess
    ret

msg:
    .ascii "Hello, world!"
    .byte 10
    .byte 0
