extern printf, atoi

section .data
fmt : db "%d", 10, 0
float_print : db "%g", 10, 0
partie_reelle : db "%g ", 0
coord_i : db "%g i +", 0
coord_j : db "%g j +", 0
coord_k : db "%g k +", 10, 0
argc : dq 0
argv : dq 0
y : dq 0
x : dq 0

section .text
global main
main : 
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    
        mov rbx, [argv]
        mov rdi, [rbx + 8]
        xor rax, rax
        call atoi
        mov [x], rax
        
    
        mov [rax], 3

        mov [y], rax        
        
    mov rax, [x]

    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret