extern printf, atoi
section .data
int_fmt : db "%d", 10, 0
float_fmt : db "%g", 10, 0
argc : dq 0
argv : dq 0
DECL_VARS

section .text
global main
main : 
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    mov rbp, rsp

    INIT_VARS
    BODY

    RETURN
    END

    pop rbp
    ret

