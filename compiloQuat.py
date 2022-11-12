import lark

#######################
###### GRAMMAIRE ######
#######################

grammaire = lark.Lark(r"""
exp : SIGNED_FLOAT "+" SIGNED_FLOAT "i" "+" SIGNED_FLOAT "j" "+" SIGNED_FLOAT "k"     -> exp_quat
| SIGNED_FLOAT                   -> exp_float
| SIGNED_NUMBER                  -> exp_entier
| IDENTIFIER                     -> exp_var
| exp OPBIN exp                  -> exp_opbin
| "(" exp ")"                    -> exp_par
| "re(" exp ")"                  -> exp_reel
| "im(" exp ")"                  -> exp_im
| exp ".i"                       -> exp_i
| exp ".j"                       -> exp_j
| exp ".k"                       -> exp_k
com : IDENTIFIER "=" exp ";"     -> assignation
| "if" "(" exp ")" "{" bcom "}"  -> if
| "while" "(" exp ")" "{" bcom "}"  -> while
| "print" "(" exp ")"               -> print
bcom : (com)*
prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";"  "}"
var_list :                       -> vide
| IDENTIFIER (","  IDENTIFIER)*  -> aumoinsune
IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/
OPBIN : /[+\-*>]/
%import common.WS
%import common.SIGNED_NUMBER
%import common.SIGNED_FLOAT
%ignore WS
""",start="prg")

# TODO ?
# com
#| "re(" IDENTIFIER ")" "=" exp ";"  -> ass_reel
#| IDENTIFIER ".i" "=" exp ";"       -> ass_i
#| IDENTIFIER ".j" "=" exp ";"       -> ass_j
#| IDENTIFIER ".k" "=" exp ";"       -> ass_k

########################
#### PRETTY PRINTER ####
########################

def pp_exp(e):
    if e.data == "exp_quat":
        return f"{e.children[0].value} + {e.children[1].value}i + {e.children[2].value}j + {e.children[3].value}k"
    elif e.data == "exp_float":
        return f"{e.children[0].value}"
    elif e.data == "exp_entier":
        return f"{e.children[0].value}"
    elif e.data == "exp_var":
        return f"{e.children[0].value}"
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "exp_opbin":
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
    elif e.data == "exp_reel":
        return f"re({pp_exp(e.children[0])})"
    elif e.data == "exp_im":
        return f"im({pp_exp(e.children[0])})"
    elif e.data == "exp_i":
        return f"{pp_exp(e.children[0])}.i"
    elif e.data == "exp_j":
        return f"{pp_exp(e.children[0])}.j"
    elif e.data == "exp_k":
        return f"{pp_exp(e.children[0])}.k"
    else:
        return "Cas non traité"


def pp_com(c):
    if c.data == "assignation":
        return f"{c.children[0].value} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        x = f"\n{indent(pp_bcom(c.children[1]))}"
        return f"if ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "while":
        x = f"\n{indent(pp_bcom(c.children[1]))}"
        return f"while ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"
    else:
        return "Cas non traité"

def pp_bcom(bc):
    return "\n".join([pp_com(c) for c in bc.children])

def pp_var_list(vl):
    return ", ".join([t.value for t in vl.children])

def pp_prg(p):
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main(%s) {\n%s    return(%s);\n}" % (L, indent(C), R)

def indent(s: str, amplitude = 4):
    """
    Indents a string, i.e adds amplitude * " " at the beginning of each line.
    """
    indent_s = amplitude * " "
    words = s.split("\n")
    if not words[-1]:
        words.pop()
    return indent_s + f"\n{indent_s}".join(words) + "\n"


########################
###### ASSEMBLEUR ######
########################

rsp = 0

def empty():
    global rsp
    s = f"""
    add rsp, {rsp}
    """
    rsp = 0
    return s

###############
#### FLOAT ####
###############

def float_get_in_st_from_tree_exp(e):
    ## Récupère la valeur de l'expression représentant un float et l'enregistre dans rax,
    ##  puis l'empile dans la pile stack du ALU et enfin dans la pile stack du FPU
    ## Incrémnte rsp de 8 pour libérer la place qui a été allouée au float au top de la pile stack du ALU
    s = f"""
    mov rax, __float64__({e.children[0].value})
    push rax
    fld qword [rsp]
    add rsp,8
    """
    return s

def float_transfer_st_to_storage():
    ## As mov [rsp], st
    ## Dépile le float au top de la pile stack du FPU et le sauvegarde dans la case de la pile stack ALU
    ##  dont l'adresse est désignée par la valeur au top de la pile ALU
    ## --> Récupère (sans dépiler rsp) l'adresse de stockage et l'enregistre comme valeur de rbx
    ## --> Dépile la pile stack du FPU et sauvegarde le float récupérée à l'adresse enregistrée dans rbx
    s = """
    mov rbx, [rsp]
    fstp qword [rbx]
    add rsp, 8
    """
    global rsp
    rsp += 8
    return s

def float_print_from_st():
    ## Print un float enregistré au top st(0) de la pile stack FPU
    s = f"""
    {empty()}
    """
    s += """
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf

    finit
    """
    return s


###############
# QUATERNIONS #
###############

# Pour être certain qu'il y a assez de place pour stocker chaque quaternion
# On initialise, au début du programme, un dictionnaire avec pour clés toutes
#  les variables utilisées au cours du programme, et pour chacune la valeur 
#  sera une adresse relative à rbp le bas de la pile stack ALU, décalée de 
#  32 bytes par rapport à la précédente :
type_des_variables = {}
positions_des_variables = {}

# Les coordonnées d'un quaternion sont toujours enregistrées dans les piles stack
#  selon l'ordre croissant des adresses :
#  la partie réelle dans la case d'adresse la plus petite (st(0) ou [rax] ou [rsp])
#  la coordonnée k dans la case d'adresse la plus grande (st(3) ou [rax + 24] ou [rsp + 24])


def quat_get_in_st_from_tree_exp(e):
    ## Récupère la valeur de l'expression représentant un quaternion et pour chaque coordonnée :
    ##  enregistre la coordonnée dans rax, l'empile dans la pile stack du ALU puis dans la pile stack du FPU
    ## Pour chaque coordonnée : 
    ## --> enregistre la coordonnée dans rax et l'empile dans la pile stack du ALU
    ## --> met à jour st(0) par rapport à la coordonnée enregistrée dans [rsp]
    ## Puis incrémnte rsp de 32 pour libérer la place qui a été allouée aux coordonnées au top de la pile stack du ALU
    r,i,j,k = [e.children[f].value for f in range(4)]
    s = f"""
    mov rax, __float64__({k})
    push rax
    fld qword [rsp]
    """
    s += f"""
    mov rax, __float64__({j})
    push rax
    fld qword [rsp]
    """
    s += f"""
    mov rax, __float64__({i})
    push rax
    fld qword [rsp]
    """
    s += f"""
    mov rax, __float64__({r})
    push rax
    fld qword [rsp]
    """
    s += """
    add rsp, 32
    """
    return s

def quat_transfer_st_to_storage():
    ## As mov [rsp], st
    ## Dépile le quaternion au top de la pile stack du FPU et le sauvegarde dans la case de la pile stack ALU
    ##  dont l'adresse est désignée par la valeur au top de la pile ALU
    ## --> Récupère (sans dépiler rsp) l'adresse de stockage et l'enregistre comme valeur de rbx
    ## --> dépile la partie réelle enregistrée en st(0) et l'enregistre en [rbx]
    ## --> dépile la coordonnée i enregistrée autrefois en st(1) et l'enregistre en [rbx + 8]
    ## --> dépile la coordonnée j enregistrée autrefois en st(2) et l'enregistre en [rbx + 16]
    ## --> dépile la coordonnée k enregistrée autrefois en st(3) et l'enregistre en [rbx + 24]
    s = f"""
    mov rbx, [rsp]
    fstp qword [rbx]
    fstp qword [rbx + 8]
    fstp qword [rbx + 16]
    fstp qword [rbx + 24]
    add rsp, 8
    """
    global rsp
    rsp += 8
    return s

def quat_get_in_st_from_storage():
    ## As mov st, [rsp]
    ## Li le quaternion sauvegardé à l'adresse indiqué par [rsp] et l'empile dans la pile stack du FPU
    ## --> Récupère (sans dépiler rsp) l'adresse de stockage et l'enregistre comme valeur de rbx
    ## --> met à jour st(0) (qui deviendra st(3)) par rapport à la coordonnée k enregistrée dans [rbx + 24]
    ## --> met à jour st(0) (qui deviendra st(2)) par rapport à la coordonnée j enregistrée dans [rbx + 16]
    ## --> met à jour st(0) (qui deviendra st(1)) par rapport à la coordonnée i enregistrée dans [rbx + 8]
    ## --> met à jour st(0) par rapport à la partie réelle enregistrée dans [rbx]
    s = f"""
    mov rbx, [rsp]
    fld qword [rbx + 24]
    fld qword [rbx + 16]
    fld qword [rbx + 8]
    fld qword [rbx]
    add rsp, 8
    """
    global rsp
    rsp += 8
    return s

def quat_print_from_st():
    # Print un quaternion enregistré dans la pile stack du FPU (et le dépile)
    s = f"""
    {empty()}
    """
    
    s += f"""
    mov rdi, partie_reelle
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    """

    s += f"""
    mov rdi, coord_i
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    """

    s += f"""
    mov rdi, coord_j
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    """

    s += f"""
    mov rdi, coord_k
    sub rsp, 8
    fstp qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
    """

    s += f"""
    finit
    """
    
    return s

def quat_add(e):
    # Calcule le quaternion résultat de l'expression 1 et l'empile au top de la pile stack du FPU
    E1 = asm_exp(e.children[0])
    # Calcule le quaternion résultat de l'expression 2 et l'empile au top de la pile stack du FPU
    E2 = asm_exp(e.children[2])
    # On a alors r1 en st(4), i1 en st(5), j1 en st(6), k1 en st(7), r2 en st(0), i2 en st(1), j2 en st(2) et k2 en st(3)
    s = f"""
    finit
    {E1}
    {E2}
    faddp st4,st0       ; on obtient r1+r2 en st(4) puis on pop donc tout se décale d'un cran (r1+r2 --> en st3)
    faddp st4,st0       ; on obtient i1+i2 en st(4) puis on pop donc tout se décale d'un cran (r1+r2 --> en st2, i1+i2 --> en st3)
    faddp st4,st0       ; on obtient j1+j2 en st(4) puis on pop donc tout se décale d'un cran (r1+r2 --> en st1, i1+i2 --> en st2, j1+j2 --> en st3)
    faddp st4,st0       ; on obtient k1+k2 en st(4) puis on pop donc tout se décale d'un cran (r1+r2 --> en st0, i1+i2 --> en st1, j1+j2 --> en st2, k1+k2 --> en st3)
    """
    return s

def quat_sub(e):
    # Calcule le quaternion résultat de l'expression 1 et l'empile au top de la pile stack du FPU
    E1 = asm_exp(e.children[0])
    # Calcule le quaternion résultat de l'expression 2 et l'empile au top de la pile stack du FPU
    E2 = asm_exp(e.children[2])
    # On a alors r1 en st(4), i1 en st(5), j1 en st(6), k1 en st(7), r2 en st(0), i2 en st(1), j2 en st(2) et k2 en st(3)
    s = f"""
    finit
    {E1}
    {E2}
    fsubp st4,st0       ; on obtient r1-r2 en st(4) puis on pop donc tout se décale d'un cran (r1-r2 --> en st3)
    fsubp st4,st0       ; on obtient i1-i2 en st(4) puis on pop donc tout se décale d'un cran (r1-r2 --> en st2, i1-i2 --> en st3)
    fsubp st4,st0       ; on obtient j1-j2 en st(4) puis on pop donc tout se décale d'un cran (r1-r2 --> en st1, i1-i2 --> en st2, j1-j2 --> en st3)
    fsubp st4,st0       ; on obtient k1-k2 en st(4) puis on pop donc tout se décale d'un cran (r1-r2 --> en st0, i1-i2 --> en st1, j1-j2 --> en st2, k1-k2 --> en st3)
    """
    return s

def quat_mult(e):
    # Calcule le quaternion résultat de l'expression 2 et l'empile au top de la pile stack du FPU
    E2 = asm_exp(e.children[0])
    # Calcule le quaternion résultat de l'expression 1 et l'empile au top de la pile stack du FPU
    E1 = asm_exp(e.children[2])
    s = f"""
    finit

    {E2}
    {E1}
    """
    # On a alors r1 en st(0), i1 en st(1), j1 en st(2), k1 en st(3), r2 en st(4), i2 en st(5), j2 en st(6) et k2 en st(7)
    
    
    # Le résultat de (r1 + i1.i + j1.j + k1.k)*(r2 + i2.i + j2.j + k2.k) est
    # r1*r2 - i1*i2 - j1*j2 - k1*k2 +
    # (r1*i2 + i1*r2 + j1*k2 - k1*j2).i +
    # (r1*j2 - i1*k2 + j1*r2 + k1*i2).j +
    # (r1*k2 + i1*j2 - j1*i2 + k1*r2). k

    ## On sauvegarde les coordonnées du quaternion résultat 1 au top de la pile stack du ALU
    ## On peut ensuite empiler 4 nouveaux float, utilisés pour faire les calculs, au top de la pile stack du FPU
    global rsp
    rsp -= 32
    s += f"""
    sub rsp, 32
    fstp qword [rsp]        ; enregistre r1
    fstp qword [rsp + 8]    ; enregistre i1
    fstp qword [rsp + 16]   ; enregistre j1
    fstp qword [rsp + 24]   ; enregistre k1
    """
    # On a alors k1 en st(0), r2 en st(1), i2 en st(2), j2 en st(3) et k2 en st(4)
    
    ## Calcul de la partie réelle
    s += f"""
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
    """
    rsp -= 8

    ## Calcul de la coordonnée i
    s += f"""
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
    """
    rsp -= 8

    ## Calcul de la coordonnée j
    s += f"""
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
    """
    rsp -= 8
    
    ## Calcul de la coordonnée k
    # (r1*k2 + i1*j2 - j1*i2 + k1*r2). k
    s += f"""
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
    """
    rsp -= 8

    # Vidage de la pile stack du FPU
    s += f"""
    finit
    """

    # Empilage des nouvelles coordonnées dans la pile stack du FPU
    s += """
    fld qword [rsp]         ; empilage de la coordonnée k
    fld qword [rsp + 8]     ; empilage de la coordonnée j
    fld qword [rsp + 16]    ; empilage de la coordonnée i
    fld qword [rsp + 24]    ; empilage de la partie réelle
    
    add rsp, 64     ; vidage de la pile stack du ALU des float enregistrés pour les calculs
    """
    rsp += 64
    return s

def type_exp(e):
    global type_des_variables
    if e.data == "exp_quat" :
        return "quat"
    elif e.data == "exp_float":
        return "float"
    elif e.data == "exp_entier":
        return "entier"
    elif e.data == "exp_var":
        try:
            return f"{type_des_variables[e.children[0].value]}"
        except KeyError:
            # La variable n'a pas été assignée avant d'être utilisée dans une expression
            # c'est donc que la variable a été donnée en argument
            # les seuls arguments possibles ici sont des entiers
            type_des_variables[e.children[0].value] = "entier"
            return "entier"

    elif e.data == "exp_opbin":
        return type_exp(e.children[0])
    elif e.data == "exp_par":
        return type_exp(e.children[0])
    elif e.data in {"exp_reel","exp_i","exp_j","exp_k"}:
        return "float"
    elif e.data == "exp_im":
        return "quat"
    else:
        "Cas non traité"

op = {'+' : 'add', '-' : 'sub', '*' : 'imul'}
op_float = {'+' : 'faddp', '-' : 'fsubp', '*' : 'fmulp'}

def asm_exp(e):
    if e.data == "exp_quat":
        # Enregistre les coordonnées du quaternion dans la pile stack du FPU
        return quat_get_in_st_from_tree_exp(e)

    elif e.data == "exp_entier":
        return f"mov rax, {e.children[0].value}\n"

    elif e.data == "exp_float":
        # Enregistre le float au top de la pile stack du FPU
        return float_get_in_st_from_tree_exp(e)

    elif e.data == "exp_var":

        position_var = positions_des_variables[e.children[0].value]

        try:
            type_var = type_des_variables[e.children[0].value]
            type_var = type_des_variables[e.children[2].value]
        except:
            # On effectue des opérations entre argument(s) et entiers
            return f"""
            mov rax, rbp
            sub rax, {position_var}
            mov rax, [rax]
            """
            
        if type_var == "entier":
            ## Lit dans le dictionnaire des adresses des variables l'adresse de la variable
            ##   pour pouvoir obtenir la valeur de la variable et l'enregistrer dans rax
            return f"""
            mov rax, rbp
            sub rax, {position_var}
            mov rax, [rax]
            """
        
        elif type_var == "float":
            ## Lit le float enregistré à l'adresse de la variable et l'empile au top de la pile stack du FPU
            s = f"""
            mov rax, rbp
            sub rax, {position_var}
            fld qword [rax]
            """
            return s

        elif type_var == "quat":
            ## Enregistre les coordonnées du quaternion désigné par la variable dans la pile stack du FPU :
            s = f"""
            mov rax, rbp
            sub rax, {position_var}
            push rax
            {quat_get_in_st_from_storage()}
            """
            global rsp
            rsp -= 8
            return s
        
        else:
            return "Cas non traité"

    elif e.data == "exp_par":
        return asm_exp(e.children[0])

    elif e.data == "exp_opbin":
        type_op = type_exp(e.children[0]) 
        # On ne peut effectuer des opérations binaires que sur des objets de même type !

        if type_op == "entier":
            E1 = asm_exp(e.children[0])
            E2 = asm_exp(e.children[2])
            return f"""
            {E2}
            push rax
            {E1}
            pop rbx
            {op[e.children[1].value]} rax, rbx
            """
        
        elif type_op == "float":
            ## Calcule le résultat de l'opération binaire sur les float 
            ##  et enregistre le résultat dans st(0), sans laisser de valeur parasite dans la pile
            # --> calcule le float résultat de l'expression 1 et l'empile en st(0)
            # --> calcule le float résultat de l'expression 2 et l'empile en st(0)
            # --> E1 devient st(1)
            E1 = asm_exp(e.children[0])
            E2 = asm_exp(e.children[2])
            # --> calcule st1 = st1 op_float st0 puis dépile donc le résultat s'enregistre en st(0), la valeur parasite étant dépilée
            s = f"""
            {E1}
            {E2}
            {op_float[e.children[1].value]} st1, st0
            """
            return s
        
        elif type_op == "quat":
            ## Calcule les résultats de chaque expression puis le résultat de l'opération
            ##   sur celles-ci et l'empile au top de la pile stack du FPU
            if(e.children[1].value == '+'):
                return quat_add(e)
            elif(e.children[1].value == '-'):
                return quat_sub(e)
            elif(e.children[1].value == '*'):
                return quat_mult(e)
            else:
                return "Cas non traité"
        
        else:
            return "Cas non traité"

    elif e.data == "exp_reel":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        E = asm_exp(e.children[0])
        # On enregistre sa partie réelle au top de la pile stack FPU
        #   : elle y est déjà
        s = f"""
        {E}
        """
        return s

    elif e.data == "exp_i":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        E = asm_exp(e.children[0])
        # On enregistre sa coordonnée i au top de la pile stack FPU : on dépile une fois
        s = f"""
        {E}
        sub rsp, 8
        fstp qword [rsp]
        add rsp, 8
        """
        return s

    elif e.data == "exp_j":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        E = asm_exp(e.children[0])
        # On enregistre sa coordonnée j au top de la pile stack FPU : on dépile 2 fois
        s = f"""
        {E}
        sub rsp, 8
        fstp qword [rsp]
        fstp qword [rsp]
        add rsp, 8
        """
        return s
   
    elif e.data == "exp_k":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        E = asm_exp(e.children[0])
        # On enregistre sa coordonnée k au top de la pile stack FPU : on dépile 3 fois
        s = f"""
        {E}
        sub rsp, 8
        fstp qword [rsp]
        fstp qword [rsp]
        fstp qword [rsp]
        add rsp, 8
        """
        return s

    elif e.data == "exp_im":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        E = asm_exp(e.children[0])
        # Le résultat que l'on retourne est un quaternion sans sa partie réelle, donc on
        #   annule simplement sa partie réelle, enregistrée en st(0)
        s = f"""
        {E}
        fsub st0, st0
        """
        return s

    else :
        return "Cas non traité"


cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt


def asm_com(c):
    global type_des_variables

    if c.data == "assignation":
        type_var = type_exp(c.children[1])
        type_des_variables[c.children[0].value] = type_var

        adresse = positions_des_variables[c.children[0].value]

        if type_var == "entier":
            E = asm_exp(c.children[1])
            return f"""
            {E}
            mov rbx, rbp
            sub rbx, {adresse}
            mov [rbx], rax
            """
        
        elif type_var == "float":
            # Stockage du float résultat de l'expression dans la pile stack du FPU
            exp = asm_exp(c.children[1])
            # Stockage de l'adresse de la variable au top de la pile stack du ALU
            stock = f"""
            mov rax, rbp
            sub rax, {adresse}
            push rax"""
            global rsp
            rsp -= 8
            # Enregistrement du float dans la pile stack du ALU à l'adresse prévue pour la variable
            stack = float_transfer_st_to_storage()
            s = f"""
            {exp}
            {stock}
            {stack}

            finit
            """
            return s

        elif type_var == "quat" :
            # Stockage du quaternion résultat de l'expression dans la pile stack du FPU
            exp = asm_exp(c.children[1])
            # Stockage de l'adresse de la variable au top de la pile stack du ALU
            stock = f"""
            mov rax, rbp
            sub rax, {adresse}
            push rax"""
            rsp -= 8
            # Enregistrement des coordonnées du quaternion dans la pile stack du ALU à l'adresse prévue pour la variable
            stack = f"""{quat_transfer_st_to_storage()}"""
            s = f"""
            {exp}
            {stock}
            {stack}

            finit
            """
            return s
        
        else:
            return "Cas non traité"

    elif c.data == "if":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        {E}
        cmp rax, 0
        jz fin{n}
        {C}
        fin{n} : nop
        """

    elif c.data == "while":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        debut{n} : {E}
        cmp rax, 0
        jz fin{n}
        {C}
        jmp debut{n}
        fin{n} : nop
        """

    elif c.data == "print":
        type_print = type_exp(c.children[0])

        if type_print == "entier":
            E = asm_exp(c.children[0])
            return f"""
            {E}
            mov rdi, entier_print
            mov rsi, rax
            call printf
            """
        
        elif type_print == "float":
            s = ""
            calcul = asm_exp(c.children[0])
            print = float_print_from_st()
            s += f"""
            finit
            {calcul}
            {print}
            finit
            """
            return s
        
        elif type_print == "quat":
            s = f"""
            finit
            {asm_exp(c.children[0])}
            {quat_print_from_st()}
            finit
            """
            return s
        
        else:
            return "Cas non traité"
    
    else :
        return "Cas non traité"

def asm_bcom(bc):
    return "".join([asm_com(c) for c in bc.children])

def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    
    ## Création du dictionnaire des adresses des variables
    global positions_des_variables
    positions_des_variables = {}

    variables = [v for v in vars_prg(p)]
    print(variables)
    for i in range(len(variables)) :
        positions_des_variables[f"{variables[i]}"]= (i+1)*32
    print(positions_des_variables)

    global type_des_variables
    type_des_variables = {}
    
    # Ici on ne peut passer en argument de main que des entiers    
    s = ""
    for i in range(len(p.children[0].children)):
        v = p.children[0].children[i].value
        position_var = positions_des_variables[v]
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + { 8*(i+1)}]
        xor rax, rax
        call atoi
        mov rbx, rbp
        sub rbx, {position_var}
        mov [rbx], rax
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)
    
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    

    E = asm_exp(p.children[2])
    type_ret = type_exp(p.children[2])

    if type_ret == "entier":
        print_ret = f"""
        {empty()}
        mov rdi, entier_print
        mov rsi, rax
        call printf
        """
    elif type_ret == "float":
        print_ret = float_print_from_st()
    elif type_ret == "quat":
        print_ret = quat_print_from_st()
    else:
        print_ret = "Cas non traité"
    
    s = f"""
    {E}
    {print_ret}
    """
    moule = moule.replace("RETURN", s)

    return moule


#### VARIABLES SET ####

def vars_exp(e):
    if e.data  in {"exp_quat","exp_float","exp_entier"}:
        return set()
    elif e.data ==  "exp_var":
        return { e.children[0].value }
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "exp_opbin":
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R
    elif e.data in {"exp_reel","exp_im","exp_i","exp_j","exp_k"}:
        return vars_exp(e.children[0])

def vars_com(c):
    if c.data == "assignation":
        R = vars_exp(c.children[1])
        return {c.children[0].value} | R
    elif c.data in {"if", "while"}:
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0]) 
        return E | B
    elif c.data == "print":
        return vars_exp(c.children[0])

def vars_bcom(bc):
    S = set()
    for c in bc.children:
        S = S | vars_com(c)
    return S

def vars_prg(p):
    L = set([t.value for t in p.children[0].children])
    C = vars_bcom(p.children[1])
    R = vars_exp(p.children[2])
    return L | C | R


#######################
######## TESTS ########
#######################

## Test print pour chaque expression sans enregistrement dans une variable
test1 = """
print(17)
print(1.7)
print(1.7 + 2.2 i + 2.3 j + 7.0 k)
print(3 + 5 - 9 * 2 )
print(1.3 + 4.5 - 8.9 * 1.2 )
print(1.7 + 2.2 i + 2.3 j + 7.0 k + 1.7 + 2.2 i + 2.3 j + 7.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k - 1.0 + 1.0 i + 1.0 j + 1.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k - 1.7 + 2.2 i + 2.3 j + 7.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k * 0.0 + 0.0 i + 0.0 j + 0.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k * 2.0 + 0.0 i + 0.0 j + 0.0 k)
print(1.7 + 2.2 i + 2.3 j + 7.0 k * 1.7 + 2.2 i + 2.3 j + 7.0 k)
print(1.3 + 4.5 - (8.9 * 1.2))
print(re(1.7 + 2.2 i + 2.3 j + 7.0 k))
print(im(1.7 + 2.2 i + 2.3 j + 7.0 k))
print(1.7 + 2.2 i + 2.3 j + 7.0 k .i)
print(1.7 + 2.2 i + 2.3 j + 7.0 k .j)
print(1.7 + 2.2 i + 2.3 j + 7.0 k .k)
"""

## Test d'assignation de valeurs à des variables et de la lecture de variables
test2 = """
x = 1.7 + 2.2 i + 2.3 j + 7.0 k .k;
print(x)
"""

ast = grammaire.parse(f"""
    main(){{
        {test2}
        return(1);
    }}
""")

print(pp_prg(ast))
asm = asm_prg(ast)
f = open("quat.asm", "w")
f.write(asm)
f.close()
print(type_des_variables)