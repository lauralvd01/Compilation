extern printf, atoi

section .data
entier_print : db "%d", 10, 0
float_print : db "%g", 10, 0
partie_reelle : db "%g +", 0
coord_i : db " %g i +", 0
coord_j : db " %g j +", 0
coord_k : db " %g k", 10, 0
argc : dq 0
argv : dq 0

section .text
global main
main : 
    push rbp
    mov rbp, rsp
    mov [argc], rdi
    mov [argv], rsi
    INIT_VARS
    finit
    BODY
    RETURN
    mov rsp, rbp
    pop rbp
    ret