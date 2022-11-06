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
    
            
    mov rax, __float64__(3.4)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(4.5)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(2.3)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(1.)
    push rax
    fld qword [rsp]
    
    add rsp, 32
    
            
            mov rax, rbp
            sub rax, 64
            push rax
            
    mov rbx, [rsp]
    fstp qword [rbx]
    fstp qword [rbx + 8]
    fstp qword [rbx + 16]
    fstp qword [rbx + 24]
    
            
            
    mov rax, __float64__(3.4)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(4.5)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(2.3)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(1.)
    push rax
    fld qword [rsp]
    
    add rsp, 32
    
            
            mov rax, rbp
            sub rax, 32
            push rax
            
    mov rbx, [rsp]
    fstp qword [rbx]
    fstp qword [rbx + 8]
    fstp qword [rbx + 16]
    fstp qword [rbx + 24]
    
            
            
    mov rax, __float64__(3.4)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(4.5)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(2.3)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(1.)
    push rax
    fld qword [rsp]
    
    add rsp, 32
    
            
    mov rdi, partie_reelle
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_i
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_j
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_k
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
            
            
    
    mov rax, __float64__(3.4)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(4.5)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(2.3)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(1.)
    push rax
    fld qword [rsp]
    
    add rsp, 32
    
    
    mov rax, __float64__(3.4)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(4.5)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(2.3)
    push rax
    fld qword [rsp]
    
    mov rax, __float64__(1.)
    push rax
    fld qword [rsp]
    
    add rsp, 32
    
    
    fsubp st4,st0       ; on obtient r1+r2 en st(4) puis on pop donc tout se décale d'un cran
    fsubp st4,st0       ; on obtient i1+i2 en st(4) puis on pop donc tout se décale d'un cran
    fsubp st4,st0       ; on obtient j1+j2 en st(4) puis on pop donc tout se décale d'un cran
    fsubp st4,st0       ; on obtient k1+k2 en st(4) puis on pop donc tout se décale d'un cran
    
            
    mov rdi, partie_reelle
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_i
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_j
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_k
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
            
            
            mov rax, rbp
            sub rax, 32
            push rax
            
    mov rbx, [rsp]
    fld qword [rbx + 24]
    fld qword [rbx + 16]
    fld qword [rbx + 8]
    fld qword [rbx]
    
            
            
    mov rdi, partie_reelle
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_i
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_j
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    mov rdi, coord_k
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
            
    
    mov rax, 1

    
        mov rdi, entier_print
        mov rsi, rax
        call printf
        
    
    mov rsp, rbp
    pop rbp
    ret