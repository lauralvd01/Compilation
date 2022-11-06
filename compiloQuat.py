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

#### TEST ####

print(pp_prg(grammaire.parse("""
main() {
    return (x);
}
""")))


########################
###### ASSEMBLEUR ######
########################

###############
#### FLOAT ####
###############

def float_get_in_st_from_tree_exp(e):
    ## Récupère la valeur de l'expression représentant un float et l'enregistre dans rax,
    ##  puis l'empile dans la pile stack du ALU et enfin dans la pile stack du FPU
    ## Incrémnte rsp de 8 pour libérer la place qui a été allouée au float au top de la pile stack du ALU
    s = f"""
    finit
    mov rax, __float64__({e.children[0].value})
    push rax
    fld qword [rsp]
    add rsp,8
    """
    return s

def float_get_rsp_into_st():
    ## As pop st
    ## Dépile le float au top de la pile stack du ALU et l'empile à la pile stack du FPU
    ## --> récupère le float enregistré en rsp et l'empile à la pile stack du FPU
    s = "finit\n"
    s += "fld qword [rsp]\n"
    return s

def float_get_st_into_rsp():
    ## As push st
    ## Dépile le float enregistré au top de la pile stack du FPU et l'empile dans la pile stack du ALU
    ## --> décrémente rsp pour allouer une nouvelle case à la pile stack du ALU
    ## --> lit le float enregistré en st(0) et le met en rsp
    s = "sub rsp, 8\n"
    s += "fst qword [rsp]\n"
    return s

def float_transfer_st_to_storage():
    ## As mov [rsp], st
    ## Dépile le float au top de la pile stack du FPU et le sauvegarde dans la case de la pile stack ALU
    ##  dont l'addresse est désignée par la valeur au top de la pile ALU
    ## --> Récupère (sans dépiler rsp) l'addresse de stockage et l'enregistre comme valeur de rbx
    ## --> Dépile la pile stack du FPU et sauvegarde le float récupérée à l'addresse enregistrée dans rbx
    s = "mov rbx, [rsp]\n"
    s += "fstp qword [rbx]\n"
    return s

def float_print_from_st():
    ## Print un float enregistré au top st(0) de la pile stack FPU
    s = """
    mov rdi, float_print
    sub rsp, 8
    fst qword [rsp]
    movq xmm0, qword [rsp]
    add rsp, 8
    mov rax, 1
    call printf
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
    s = "finit\n"
    s += f"mov rax, __float64__({k})\n"
    s += "push rax\n"
    s += "fld qword [rsp]\n"

    s += f"mov rax, __float64__({j})\n"
    s += "push rax\n"
    s += "fld qword [rsp]\n"

    s += f"mov rax, __float64__({i})\n"
    s += "push rax\n"
    s += "fld qword [rsp]\n"

    s += f"mov rax, __float64__({r})\n"
    s += "push rax\n"
    s += "fld qword [rsp]\n"

    s += "add rsp, 32\n"
    return s

def quat_transfer_st_to_storage():
    ## As mov [rsp], st
    ## Dépile le quaternion au top de la pile stack du FPU et le sauvegarde dans la case de la pile stack ALU
    ##  dont l'addresse est désignée par la valeur au top de la pile ALU
    ## --> Récupère (sans dépiler rsp) l'addresse de stockage et l'enregistre comme valeur de rbx
    ## --> dépile la partie réelle enregistrée en st(0) et l'enregistre en [rbx]
    ## --> dépile la coordonnée i enregistrée autrefois en st(1) et l'enregistre en [rbx + 8]
    ## --> dépile la coordonnée j enregistrée autrefois en st(2) et l'enregistre en [rbx + 16]
    ## --> dépile la coordonnée k enregistrée autrefois en st(3) et l'enregistre en [rbx + 24]
    s = "mov rbx, [rsp]\n"
    s += "fstp qword [rbx]\n"
    s += "fstp qword [rbx + 8]\n"
    s += "fstp qword [rbx + 16]\n"
    s += "fstp qword [rbx + 24]\n"

def quat_get_in_st_from_storage():
    ## As mov st, [rsp]
    ## Li le quaternion sauvegardé à l'adresse indiqué par [rsp] et l'empile dans la pile stack du FPU
    ## --> Récupère (sans dépiler rsp) l'addresse de stockage et l'enregistre comme valeur de rbx
    ## --> met à jour st(0) (qui deviendra st(3)) par rapport à la coordonnée k enregistrée dans [rbx + 24]
    ## --> met à jour st(0) (qui deviendra st(2)) par rapport à la coordonnée j enregistrée dans [rbx + 16]
    ## --> met à jour st(0) (qui deviendra st(1)) par rapport à la coordonnée i enregistrée dans [rbx + 8]
    ## --> met à jour st(0) par rapport à la partie réelle enregistrée dans [rbx]
    s = "mov rbx, [rsp]\n"
    s += "finit\n"
    s += "fld qword [rbx + 24]\n"
    s += "fld qword [rbx + 16]\n"
    s += "fld qword [rbx + 8]\n"
    s += "fld qword [rbx]\n"
    return s

def quat_print_from_st():
    # Print un quaternion enregistré dans la pile stack du FPU (et le dépile)
    s = "mov rdi, partie_reelle\n"
    s += "sub rsp, 8\n"
    s += "fstp qword [rsp]\n"
    s += "movq xmm0, qword [rsp]\n"
    s += "add rsp, 8\n"
    s += "mov rax, 1\n"
    s += "call printf\n"

    s += "mov rdi, coord_i\n"
    s += "sub rsp, 8\n"
    s += "fstp qword [rsp]\n"
    s += "movq xmm0, qword [rsp]\n"
    s += "add rsp, 8\n"
    s += "mov rax, 1\n"
    s += "call printf\n"

    s += "mov rdi, coord_j\n"
    s += "sub rsp, 8\n"
    s += "fstp qword [rsp]\n"
    s += "movq xmm0, qword [rsp]\n"
    s += "add rsp, 8\n"
    s += "mov rax, 1\n"
    s += "call printf\n"

    s += "mov rdi, coord_k\n"
    s += "sub rsp, 8\n"
    s += "fstp qword [rsp]\n"
    s += "movq xmm0, qword [rsp]\n"
    s += "add rsp, 8\n"
    s += "mov rax, 1\n"
    s += "call printf\n"
    
    return s

def quat_add(e):
    # Calcule le quaternion résultat de l'expression 2 et l'empile au top de la pile stack du FPU
    E2 = asm_exp(e.children[0])
    # Calcule le quaternion résultat de l'expression 1 et l'empile au top de la pile stack du FPU
    E1 = asm_exp(e.children[0])
    # On a alors r1 en st(1), i1 en st(2), j1 en st(3), k1 en st(4), r2 en st(5), i2 en st(6), j2 en st(7) et k2 en st(3)
    s = f"""
    {E2}
    {E1}
    fadd st0,st4
    fadd st1,st5
    fadd st2,st6
    fadd st3,st7
    """
    return s

def quat_sub(e):
    # Calcule le quaternion résultat de l'expression 2 et l'empile au top de la pile stack du FPU
    E2 = asm_exp(e.children[0])
    # Calcule le quaternion résultat de l'expression 1 et l'empile au top de la pile stack du FPU
    E1 = asm_exp(e.children[0])
    # On a alors r1 en st(1), i1 en st(2), j1 en st(3), k1 en st(4), r2 en st(5), i2 en st(6), j2 en st(7) et k2 en st(3)
    s = f"""
    {E2}
    {E1}
    fsub st0,st4
    fsub st1,st5
    fsub st2,st6
    fsub st3,st7
    """
    return s

def quat_mult(e):
    # Calcule le quaternion résultat de l'expression 2 et l'empile au top de la pile stack du FPU
    E2 = asm_exp(e.children[0])
    # Calcule le quaternion résultat de l'expression 1 et l'empile au top de la pile stack du FPU
    E1 = asm_exp(e.children[0])
    s = f"""
    {E2}
    {E1}
    """
    # On a alors r1 en st(0), i1 en st(1), j1 en st(2), k1 en st(3), r2 en st(4), i2 en st(5), j2 en st(6) et k2 en st(7)
    
    # Le résultat de (r1 + i1.i + j1.j + k1.k)*(r2 + i2.i + j2.j + k2.k) est
    # r1*r2 - i1*i2 - j1*j2 - k1*k2 +
    # (r1*i2 + i1*r2 + j1*k2 -k1*j2).i +
    # (r1*j2 + j1*r2 + k1*i2 -i1*k2).j +
    # (r1*k2 + k1*r2 + i1*j2 -j1*i2). k

    # Création de 4 float que l'on empile au top de la pile stack du FPU
    # --> Ces 4 float serviront pour les calculs de chaque coordonnée
    # --> Les coordonées des quaternions à multiplier seront donc décalées de 4
    # --> Chaque coordonnée ainsi calculée sera d'abord sauvegardée et étant empilée à la pile stack du ALU 

    s += "fld st3\n" # Push k1 en st0
    s += "fld st3\n" # Push j1 en st0
    s += "fld st3\n" # Push i1 en st0
    s += "fld st3\n" # Push r1 en st0
    # On a alors r1 en st(4), i1 en st(5), j1 en st(6), k1 en st(7), r2 en st(8), i2 en st(9), j2 en st(10) et k2 en st(11)
    
    ## Calcul de la partie réelle
    s += "fmul st0,st8\n"
    s += "fmul st1,st9\n"
    s += "fmul st2,st10\n"
    s += "fmul st3,st11\n"
    s += "fsub st0,st1\n"
    s += "fsub st0,st2\n"
    s += "fsub st0,st3\n"

    s += float_get_st_into_rsp()

    # Remise à 0
    s += "fsub st0,st0\n"
    s += "fsub st1,st1\n"
    s += "fsub st2,st2\n"
    s += "fsub st3,st3\n"

    ## Calcul de la coordonnée i
    s += "fadd st0,st4\n"
    s += "fadd st1,st5\n"
    s += "fadd st2,st6\n"
    s += "fadd st3,st7\n"

    s += "fmul st0,st9\n"
    s += "fmul st1,st8\n"
    s += "fmul st2,st11\n"
    s += "fmul st3,st10\n"
    s += "fadd st0,st1\n"
    s += "fadd st0,st2\n"
    s += "fsub st0,st3\n"

    s += float_get_st_into_rsp()

    # Remise à 0
    s += "fsub st0,st0\n"
    s += "fsub st1,st1\n"
    s += "fsub st2,st2\n"
    s += "fsub st3,st3\n"

    ## Calcul de la coordonnée j
    # (r1*j2 + j1*r2 + k1*i2 -i1*k2).j +
    s += "fadd st0,st4\n"
    s += "fadd st1,st6\n"
    s += "fadd st2,st7\n"
    s += "fadd st3,st5\n"

    s += "fmul st0,st10\n"
    s += "fmul st1,st8\n"
    s += "fmul st2,st9\n"
    s += "fmul st3,st11\n"
    s += "fadd st0,st1\n"
    s += "fadd st0,st2\n"
    s += "fsub st0,st3\n"

    s += float_get_st_into_rsp()

    # Remise à 0
    s += "fsub st0,st0\n"
    s += "fsub st1,st1\n"
    s += "fsub st2,st2\n"
    s += "fsub st3,st3\n"

    ## Calcul de la coordonnée k
    s += "fadd st0,st4\n"
    s += "fadd st1,st7\n"
    s += "fadd st2,st5\n"
    s += "fadd st3,st6\n"

    s += "fmul st0,st11\n"
    s += "fmul st1,st8\n"
    s += "fmul st2,st10\n"
    s += "fmul st3,st9\n"
    s += "fadd st0,st1\n"
    s += "fadd st0,st2\n"
    s += "fsub st0,st3\n"

    s += float_get_st_into_rsp()

    # Vidage de la pile stack du FPU
    vide = "fstp st0"*12
    s += vide

    # Empilage des nouvelles coordonnées dans la pile stack du FPU
    s += "finit\n"
    s += "fld qword [rsp]\n"
    s += "fld qword [rsp + 8]\n"
    s += "fld qword [rsp + 16]\n"
    s += "fld qword [rsp + 24]\n"
    s += "add rsp, 32\n"

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
        return f"{type_des_variables[e.children[0].value]}"
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

op = {'+' : 'add', '-' : 'sub', '*' : 'mult'}
op_float = {'+' : 'faddp', '-' : 'fsubp', '*' : 'fmultp'}

def asm_exp(e):
    if e.data == "exp_quat":
        # Enregistre les coordonnées du quaternion dans la pile stack du FPU
        return quat_get_in_st_from_tree_exp(e)

    elif e.data == "exp_entier":
        return f"mov rax, {e.children[0].value}\n"

    elif e.data == "exp_float":
        # Enregistre la valeur du float dans rax puis
        # Enregistre le float au top de la pile stack du FPU
        return float_get_in_st_from_tree_exp(e)

    elif e.data == "exp_var":
        type_var = type_des_variables[e.children[0].value]
        position_var = positions_des_variables[e.children[0].value]

        if(type_var == "entier"):
            ## Lit dans le dictionnaire des adresses des variables l'adresse de la variable
            ##   pour pouvoir obtenir la valeur de la variable et l'enregistrer dans rax
            return f"mov rax, [{position_var}]\n"

        elif(type_var == "float"):
            ## Lit le float enregistré à l'adresse de la variable et l'empile au top de la pile stack du FPU
            ## Enregistre également la valeur dans rax
            s = f"push qword [{position_var}]\n"
            s += float_get_rsp_into_st()
            s += "mov rax, qword [rsp]\n"
            return s

        elif(type_var == "quat"):
            ## Enregistre les coordonnées du quaternion désigné par la variable dans la pile stack du FPU :
            s = ""
            # Stockage de l'adresse du quaternion au top de la pile stack du ALU
            s += f"push {position_var}\n"
            # Empile au top de la pile stack du FPU les coordonées du quaternion enregistré à l'adresse indiquée
            s += quat_get_in_st_from_storage()
            return s
        else:
            return "Cas non traité"

    elif e.data == "exp_par":
        return asm_exp(e.children[0])

    elif e.data == "exp_opbin":
        type_op = type_exp(e.children[0]) # On ne peut effectuer des opérations binaires que sur des objets de même type !

        if(type_op == "entier"):
            E1 = asm_exp(e.children[0])
            E2 = asm_exp(e.children[2])
            return f"""
            {E2}
            push rax
            {E1}
            pop rbx
            {op[e.children[1].value]} rax, rbx
            """
        elif(type_op == "float"):
            ## Calcule le résultat de l'opération binaire sur les float 
            ##  et enregistre le résultat dans st(0)
            s = ""
            # Calcule le float résultat de l'expression 1 et l'empile en st(0)
            E1 = asm_exp(e.children[0])
            # Calcule le float résultat de l'expression 2 et l'empile en st(0)
            # E1 devient st(1)
            E2 = asm_exp(e.children[2])
            # Calcule st1 = st1 op_float st0 et pop st(0) donc le résultat devient le top de la pile stack du FPU
            resultat = f"{op_float[e.children[1].value]} st1, st0"
            # De plus on enregistre le float résultat dans rax
            rax = float_get_st_into_rsp()
            rax += "pop rax"
            s += f"""
            {E1}
            {E2}
            {resultat}
            {rax}
            """
            return s
        
        elif(type_op == "quat"):
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

    elif e.data == "exp_reel":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        s = asm_exp(e.children[0])
        # On enregistre sa partie réelle au top de la pile stack FPU
        #   : elle y est déjà
        # Comme le résultat est un float on enregistre également le float dans rax
        s += float_get_st_into_rsp()
        s += "pop rax\n"
        return s
    elif e.data == "exp_i":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        s = asm_exp(e.children[0])
        # On enregistre sa coordonnée i au top de la pile stack FPU : on dépile une fois
        # Et puis on lit sa valeur pour l'enregistrer dans rax
        s += "sub rsp, 8\n"
        s += "fstp qword [rsp]\n"
        s += float_get_st_into_rsp()
        s += "pop rax\n"
        return s
    elif e.data == "exp_j":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        s = asm_exp(e.children[0])
        # On enregistre sa coordonnée j au top de la pile stack FPU : on dépile 2 fois
        # Et puis on lit sa valeur pour l'enregistrer dans rax
        s += "sub rsp, 8\n"
        s += "fstp qword [rsp]\n"
        s += "fstp qword [rsp]\n"
        s += float_get_st_into_rsp()
        s += "pop rax\n"
        return s
    elif e.data == "exp_k":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        s = asm_exp(e.children[0])
        # On enregistre sa coordonnée k au top de la pile stack FPU : on dépile 3 fois
        # Et puis on lit sa valeur pour l'enregistrer dans rax
        s += "sub rsp, 8\n"
        s += "fstp qword [rsp]\n"
        s += "fstp qword [rsp]\n"
        s += "fstp qword [rsp]\n"
        s += float_get_st_into_rsp()
        s += "pop rax\n"
        return s
    elif e.data == "exp_im":
        # Le quaternion résultat de l'expression est enregistré au top de la pile stack du FPU
        s = asm_exp(e.children[0])
        # Le résultat que l'on retourne est un quaternion sans sa partie réelle, donc on
        #   annule simplement sa partie réelle, enregistrée en st(0)
        s += "fsub st0, st0\n"
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
            mov [{adresse}], rax        
            """
        elif type_var == "float":
            # Stockage du float résultat de l'expression dans la pile stack du FPU
            exp = asm_exp(c.children[1])
            # Stockage de l'adresse de la variable au top de la pile stack du ALU
            stock = f"""
            push {adresse}
            """
            # Enregistrement du float dans la pile stack du ALU à l'adresse prévue pour la variable
            stock += float_transfer_st_to_storage()
            s = f"""
            {exp}
            {stock}
            """
            return s

        elif(type_var == "quat"):
            # Stockage du quaternion résultat de l'expression dans la pile stack du FPU
            exp = asm_exp(c.children[1])
            # Stockage de l'adresse de la variable au top de la pile stack du ALU
            stock = f"push {adresse}\n"
            # Enregistrement des coordonnées du quaternion dans la pile stack du ALU à l'adresse prévue pour la variable
            stock += quat_transfer_st_to_storage()
            s = f"""
            {exp}
            {stock}
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

        if(type_print == "entier"):
            E = asm_exp(c.children[0])
            return f"""
            {E}
            mov rdi, entier_print
            mov rsi, rax
            call printf
            """
        elif(type_print == "float"):
            s = ""
            calcul = asm_exp(c.children[0])
            print = float_print_from_st()
            s += f"""
            {calcul}
            {print}
            """
            return s
        
        elif(type_print == "quat"):
            s = f"""
            {asm_exp(c.children[0])}
            {quat_print_from_st()}
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
    
    ## Création du disctionnaire des adresses des variables
    variables = [v for v in vars_prg(p)]

    global positions_des_variables
    positions_des_variables = {}
    for i in range(len(variables)) :
        positions_des_variables[f"{variables[i]}"]= f"rbp - {(i+1)*32}"
    
    # TODO : vérifier si la déclaration des variables ne change pas
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
    
    # TODO : pour le moment on ne peut mettre en argument que des entiers
    s = ""
    for i in range(len(p.children[0].children)):
        v = p.children[0].children[i].value
        adresse = positions_des_variables[v]
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + { 8*(i+1)}]
        xor rax, rax
        call atoi
        mov [{adresse}], rax
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)
    
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    
    E = asm_exp(p.children[2])
    type_ret = type_exp(p.children[2])
    if type_ret == "entier":
        print = f"""
        mov rdi, entier_print
        mov rsi, rax
        call printf
        """
    elif type_ret == "float":
        print = float_print_from_st()
    elif type_ret == "quat":
        print = quat_print_from_st()
    else:
        print = "Cas non traité"
    s = f"""
    {E}
    {print}
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


#### TESTS ####

ast = grammaire.parse("""
    main(x){
        print(3.1 + 2.4i + 3.6j + 5.4k)
        return(4.5);
    }
""")
asm = asm_prg(ast)
f = open("quat.asm", "w")
f.write(asm)
f.close()
