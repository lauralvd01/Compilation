extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
y : dq 0
a : dq 0
g : dq 0

section .text
global main
main : 
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    mov rbp, rsp

    
        mov rbx, [argv]
        mov rdi, [rbx + 8]
        xor rax, rax
        call atoi
        mov [rbp - 0], rax 
        sub rsp, 16
    
            mov rax, 1

            mov [rbp - 8], rax
            
            mov rax, __float64__(8.45)

            push rax
            
            mov rax, 7

            mov [rbp - 0], rax
            
            mov rax, 3

            mov [rbp - 16], rax
            
            mov rax, 6

            push rax
            

    mov rax, [rbp - 32]

    pop rbx
pop rbx
pop rbx
pop rbx

    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret

