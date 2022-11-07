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
            sub rax, 32
            push rax
            
    mov rbx, [rsp]
    fstp qword [rbx]
    fstp qword [rbx + 8]
    fstp qword [rbx + 16]
    fstp qword [rbx + 24]
    

            finit
            
            
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
    
    finit
    
            
            
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
    

    faddp st4,st0       ; on obtient r1+r2 en st(4) puis on pop donc tout se décale d'un cran
    faddp st4,st0       ; on obtient i1+i2 en st(4) puis on pop donc tout se décale d'un cran
    faddp st4,st0       ; on obtient j1+j2 en st(4) puis on pop donc tout se décale d'un cran
    faddp st4,st0       ; on obtient k1+k2 en st(4) puis on pop donc tout se décale d'un cran
    
            
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
    
    finit
    
            
            
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
    
    finit
    
            
            
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
    
    
    sub rsp, 32
    fstp qword [rsp]        ; enregistre r1
    fstp qword [rsp + 8]    ; enregistre i1
    fstp qword [rsp + 16]   ; enregistre j1
    fstp qword [rsp + 24]   ; enregistre k1
    
    fld qword [rsp + 24]  ; push k1 en st(0), r2 en st(1), i2 en st(2), j2 en st(3), k2 en st(4)
    fmul st0,st4

    fld qword [rsp + 16] ; push j1 en st(0), k1*k2 en st(1), r2 en st(2), i2 en st(3), j2 en st(4), k2 en st(5)
    fmul st0,st4
    
    fld qword [rsp + 8] ; push i1 en st(0), j1*j2 en st(1), k1*k2 en st(2), r2 en st(3), i2 en st(4), j2 en st(5), k2 en st(6)
    fmul st0,st4
    
    fld qword [rsp] ; push r1 en st(0), i1*i2 en st(1), j1*j2 en st(2), k1*k2 en st(3), r2 en st(4), i2 en st(5), j2 en st(6), k2 en st(7)
    fmul st0,st4
    
    fsub st0,st1
    fsub st0,st2
    fsub st0,st3

    sub rsp, 8
    fstp qword [rsp]    ; enregistre r1*r2 - i1*i2 - j1*j2 - k1*k2

    sub rsp, 8
    fstp qword [rsp]    ; dépile i1*i2
    fstp qword [rsp]    ; on dépile j1*j2
    fstp qword [rsp]    ; on dépile k1*k2
    add rsp, 8 
    
    fld qword [rsp + 32]  ; push k1 en st(0), r2 en st(1), i2 en st(2), j2 en st(3), k2 en st(4)
    fmul st0,st3

    fld qword [rsp + 24] ; push j1 en st(0), k1*j2 en st(1), r2 en st(2), i2 en st(3), j2 en st(4), k2 en st(5)
    fmul st0,st5
    
    fld qword [rsp + 16] ; push i1 en st(0), j1*k2 en st(1), k1*j2 en st(2), r2 en st(3), i2 en st(4), j2 en st(5), k2 en st(6)
    fmul st0,st3
    
    fld qword [rsp + 8] ; push r1 en st(0), i1*r2 en st(1), j1*k2 en st(2), k1*j2 en st(3), r2 en st(4), i2 en st(5), j2 en st(6), k2 en st(7)
    fmul st0,st5
    
    fadd st0,st1
    fadd st0,st2
    fsub st0,st3

    sub rsp, 8
    fstp qword [rsp]    ; enregistre r1*i2 - i1*r2 - j1*k2 - k1*j2

    sub rsp, 8
    fstp qword [rsp]    ; dépile i1*r2
    fstp qword [rsp]    ; on dépile j1*k2
    fstp qword [rsp]    ; on dépile k1*j2
    add rsp, 8 
    
    fld qword [rsp + 40]  ; push k1 en st(0), r2 en st(1), i2 en st(2), j2 en st(3), k2 en st(4)
    fmul st0,st2

    fld qword [rsp + 32] ; push j1 en st(0), k1*i2 en st(1), r2 en st(2), i2 en st(3), j2 en st(4), k2 en st(5)
    fmul st0,st2
    
    fld qword [rsp + 24] ; push i1 en st(0), j1*r2 en st(1), k1*i2 en st(2), r2 en st(3), i2 en st(4), j2 en st(5), k2 en st(6)
    fmul st0,st6
    
    fld qword [rsp + 16] ; push r1 en st(0), i1*k2 en st(1), j1*r2 en st(2), k1*i2 en st(3), r2 en st(4), i2 en st(5), j2 en st(6), k2 en st(7)
    fmul st0,st6
    
    fsub st0,st1
    fadd st0,st2
    fadd st0,st3

    sub rsp, 8
    fstp qword [rsp]    ; enregistre r1*j2 - i1*k2 - j1*r2 - k1*i2

    sub rsp, 8
    fstp qword [rsp]    ; dépile i1*k2
    fstp qword [rsp]    ; on dépile j1*r2
    fstp qword [rsp]    ; on dépile k1*i2
    add rsp, 8 
    
    fld qword [rsp + 48]  ; push k1 en st(0), r2 en st(1), i2 en st(2), j2 en st(3), k2 en st(4)
    fmul st0,st1

    fld qword [rsp + 40] ; push j1 en st(0), k1*r2 en st(1), r2 en st(2), i2 en st(3), j2 en st(4), k2 en st(5)
    fmul st0,st3
    
    fld qword [rsp + 32] ; push i1 en st(0), j1*i2 en st(1), k1*r2 en st(2), r2 en st(3), i2 en st(4), j2 en st(5), k2 en st(6)
    fmul st0,st5
    
    fld qword [rsp + 24] ; push r1 en st(0), i1*j2 en st(1), j1*i2 en st(2), k1*r2 en st(3), r2 en st(4), i2 en st(5), j2 en st(6), k2 en st(7)
    fmul st0,st7
    
    fadd st0,st1
    fsub st0,st2
    fadd st0,st3

    sub rsp, 8
    fstp qword [rsp]    ; enregistre r1*k2 - i1*j2 - j1*i2 - k1*r2

    sub rsp, 8
    fstp qword [rsp]    ; dépile i1*j2
    fstp qword [rsp]    ; on dépile j1*i2
    fstp qword [rsp]    ; on dépile k1*r2
    add rsp, 8 
    
    finit
    
    fld qword [rsp]         ; empilage de la coordonnée k
    fld qword [rsp + 8]     ; empilage de la coordonnée j
    fld qword [rsp + 16]    ; empilage de la coordonnée i
    fld qword [rsp + 24]    ; empilage de la partie réelle
    
    add rsp, 64     ; vidage de la pile stack du ALU des float enregistrés pour les calculs
    
            
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
    
        
            
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf

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
    
        fsub st0, st0
        
            
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
    
        sub rsp, 8
        fstp qword [rsp]
        add rsp, 8
        
            
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf

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
    
        sub rsp, 8
        fstp qword [rsp]
        fstp qword [rsp]
        add rsp, 8
        
            
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf

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
    
        sub rsp, 8
        fstp qword [rsp]
        fstp qword [rsp]
        fstp qword [rsp]
        add rsp, 8
        
            
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf

    finit
    
            
    
    mov rax, 1

    
        mov rdi, entier_print
        mov rsi, rax
        call printf
        
    
    mov rsp, rbp
    pop rbp
    ret