extern printf, atoi

section .data
entier_print : db "%d", 10, 0
float_print : db "%g", 10, 0
partie_reelle : db "%g ", 0
coord_i : db "%g i +", 0
coord_j : db "%g j +", 0
coord_k : db "%g k +", 10, 0
argc : dq 0
argv : dq 0
x : dq 0

section .text
global main
main : 
    push rbp
    mov rbp, rsp
    mov [argc], rdi
    mov [argv], rsi
    
        mov rbx, [argv]
        mov rdi, [rbx + 8]
        xor rax, rax
        call atoi
        mov [rbp - 32], rax
        
    
            finit
mov rax, __float64__(5.4)
push rax
fld qword [rsp]
mov rax, __float64__(3.6)
push rax
fld qword [rsp]
mov rax, __float64__(2.4)
push rax
fld qword [rsp]
mov rax, __float64__(3.1)
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
    mov rax, __float64__(4.5)
    push rax
    fld qword [rsp]
    add rsp,8
    
    
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    
    
    mov rsp, rbp
    pop rbp
    ret