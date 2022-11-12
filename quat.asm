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
    
    finit
    
            
        
    mov rax, __float64__(7.0)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(2.3)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(2.2)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(1.7)
    push rax
    fld qword [rsp]
    
    add rsp, 32
    
        sub rsp, 8
        fstp qword [rsp]
        fstp qword [rsp]
        fstp qword [rsp]
        add rsp, 8
        
            
            mov rax, rbp
            sub rax, 32
            push rax
            
    mov rbx, [rsp]
    fstp qword [rbx]
    add rsp, 8
    

            finit
            
            finit
            
            mov rax, rbp
            sub rax, 32
            mov rax, [rax]
            
            
    
    add rsp, 0
    
    
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf

    finit
    
            finit
            
    
    mov rax, 1

    
        
    add rsp, 0
    
        mov rdi, entier_print
        mov rsi, rax
        call printf
        
    
    mov rsp, rbp
    pop rbp
    ret