extern printf, atoi
section .data
int_fmt : db "%d", 10, 0
float_fmt : db "%g", 10, 0
argc : dq 0
argv : dq 0
a : dq 0
x : dq 0
y : dq 0
i : dq 0

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
        
        mov rbx, [argv]
        mov rdi, [rbx + 16]
        xor rax, rax
        call atoi
        mov [rbp - 16], rax 
        sub rsp, 24
    
            mov rax, 1

            mov [rbp - 24], rax
            
            
            mov rax, __float64__(4.7)
            push rax
            fld qword [rsp]
            mov rax, __float64__(1.0)
            push rax
            fld qword [rsp]
            fadd st0, st1
            fstp qword [rsp]
            pop rax
            add rsp, 8
            
            push rax
            
        mov rax, [rbp - 32]

         movq xmm0, qword rax   ; floating point in str
        mov rdi, float_fmt              ; address of format string
        mov rax, 1                  ; 1 floating point argument to printf
        call printf

        
            mov rax, __float64__(1.5)
            push rax
            fld qword [rsp]
            mov rax, __float64__(3.5)
            push rax
            fld qword [rsp]
            fadd st0, st1
            fstp qword [rsp]
            pop rax
            add rsp, 8
            
         movq xmm0, qword rax   ; floating point in str
        mov rdi, float_fmt              ; address of format string
        mov rax, 1                  ; 1 floating point argument to printf
        call printf


    mov rax, [rbp - 16]

    pop rbx
pop rbx
pop rbx
pop rbx


    pop rbp
    ret

