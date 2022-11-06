extern printf, atoi
section .data
int_fmt : db "%d", 10, 0
float_fmt : db "%g", 10, 0
argc : dq 0
argv : dq 0
a : dq 0
i : dq 0
x : dq 0
y : dq 0

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
        mov [rbp - 16], rax 
        
        mov rbx, [argv]
        mov rdi, [rbx + 16]
        xor rax, rax
        call atoi
        mov [rbp - 24], rax 
        sub rsp, 24
    
            mov rax, 4

            mov [rbp - 0], rax
            
            mov rax, 0

            mov [rbp - 8], rax
            
        debut1 : mov rax, [rbp - 16]

        cmp rax, 0
        jz fin1
        
            mov rax, __float64__(2.64)

            push rax
            
            
        mov rax, 1

        push rax
        mov rax, [rbp - 8]

        pop rbx
        add rax, rbx
        
            mov [rbp - 8], rax
            
            
        mov rax, 1

        push rax
        mov rax, [rbp - 16]

        pop rbx
        sub rax, rbx
        
            mov [rbp - 16], rax
            
        jmp debut1
fin1 : nop                   

        mov rax, [rbp - 8]

        mov rdi, int_fmt
        mov rsi, rax
        call printf
        
        mov rax, [rbp - 32]

         movq xmm0, qword rax   ; floating point in str
        mov rdi, float_fmt              ; address of format string
        mov rax, 1                  ; 1 floating point argument to printf
        call printf

    mov rax, [rbp - 24]

    pop rbx
pop rbx
pop rbx


    pop rbp
    ret

