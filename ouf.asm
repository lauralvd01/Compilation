extern printf, atoi
section .data
fmt : db "%d", 10, 0
float_print : db "%g", 10, 0
argc : dq 0
argv : dq 0
y : dq 0
a : dq 0

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
        mov [rbp - 8], rax 
        sub rsp, 8
        
    
            mov rax, 1

            mov [rbp - 16], rax
            
            mov rax, __float64__(8.45)

            push rax
            
            mov rax, __float64__(7.946)

            push rax
            

    mov rax, [rbp - 32]

     mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    pop rbp
    ret

