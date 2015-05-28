

mov  dx, msg      ; the address of our message in dx
mov  ah, 9        ; ah=9 - "print string" sub-function
int  33           ; call dos services
mov  ah, 0
int  33

msg: .byte "Hello, World!", 13, 10, "$"   ; $-terminated message
