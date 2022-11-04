import lark

#######################
###### GRAMMAIRE ######
#######################

grammaire = lark.Lark(r"""
exp : SIGNED_FLOAT "+" SIGNED_FLOAT "i" "+" SIGNED_FLOAT "j" "+" SIGNED_FLOAT "k"     -> exp_nombre
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

op = {'+' : 'add', '-' : 'sub', '*' : 'mult'}

########################
#### PRETTY PRINTER ####
########################

def pp_exp(e):
    if e.data == "exp_nombre":
        return f"{e.children[0].value} + {e.children[1].value}i + {e.children[2].value}j + {e.children[3].value}k"
    elif e.data == "exp_var":
        return e.children[0].value
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
    elif e.data == "exp_entier":
        return f"{e.children[0]}"
    else:
        return "Cas non autorisé actuellement"

def pp_assignation(c):
    assert(c.data == "assignation")
    str = f"{c.children[0].value} = "
    return str

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
        # TODO
        return f"print({pp_exp(c.children[0])})"

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
    x = 1. + 2.0i + 3.0j + 4.0k;
    if (x) {
        y = 4. + 2.0i +3.0j + 4.0k;
        while(y){
            i = i + 1. + 2.i + 3.j + 4.k;
        }
    }
    return (x);
}
""")))


########################
###### ASSEMBLEUR ######
########################

###############
#### FLOAT ####
###############

def float_transfer_rax_to_st():
    ## As mov st(0), rax
    ## Empile le float, enregistré dans le qword d'addresse enregistrée par rax, dans la pile Stack du FPU 
    ## --> met à jour st(0) par rapport à rax
    s = "finit\n"
    s += "fld qword [rax]\n"
    return 

def float_transfer_rsp_to_st():
    ## As pop st
    ## Dépile le float au top de la pile stack du ALU et l'empile à la pile stack du FPU
    ## --> récupère le float enregistré en rsp et l'empile à la pile stack du FPU
    ## --> incrémente rsp pour libérer la case au top de la pile stack du ALU
    s = "finit\n"
    s += "fld qword [rsp]\n"
    s += "add rsp, 8\n"
    return s

def float_transfer_st_to_rsp():
    ## As push st
    ## Dépile le float enregistré au top de la pile stack du FPU et l'empile dans la pile stack du ALU
    ## --> décrémente rsp pour allouer une nouvelle case à la pile stack du ALU
    ## --> dépile le float enregistré en st(0) et le met en rsp
    
    #s = "finit\n" Pourquoi ici non ?
    s = "sub rsp, 8\n"
    s += "fstp qword [rsp]\n"
    return s

def float_transfer_st_to_storage():
    ## As mov [rsp], st
    ## Dépile le float au top de la pile stack du FPU et le sauvegarde dans la case de la pile stack ALU
    ##  dont l'addresse est désignée par la valeur au top de la pile ALU
    ## --> Récupère (sans dépiler rsp) l'addresse de stockage et l'enregistre comme valeur de rbx
    ## --> Dépile la pile stack du FPU et sauvegarde le float récupérée à l'addresse enregistrée dans rbx

    #s = "finit\n" Pourquoi ici non ?
    s = "mov rbx, [rsp]\n"
    s += "fstp qword [rbx]\n"


###############
# QUATERNIONS #
###############

def quat_update_st_from_rax():
    ## As mov st, rax
    ## Empile le quaternion dans la pile stack du FPU
    ## --> met à jour st(0) par rapport à la partie réelle enregistrée dans [rax] (à partir de l'addresse de rax et sur 8 octets)
    ## --> met à jour st(1) par rapport à la coordonnée i enregistrée dans [rax + 8]
    ## --> met à jour st(2) par rapport à la coordonnée j enregistrée dans [rax + 16]
    ## --> met à jour st(3) par rapport à la coordonnée k enregistrée dans [rax + 24]
    s = "finit\n"
    s += "fld qword [rax]\n"
    s += "fld qword [rax + 8]\n"
    s += "fld qwprd [rax + 16]\n"
    s += "fld qword [rax + 24]\n"
    return s

def quat_update_rsp_from_st():
    ## As pu
    ## Dépile la pile stack du FPU pour enregistrer le quaternion dans la pile ALU
    ## 
    
    s = "finit\n"
    return s

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt


def asm_exp(e):
    if e.data == "exp_nombre":
        # TODO
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_entier":
        # TODO : vérifier si ça change
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var":
        # TODO
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    elif e.data == "exp_opbin":
        # TODO
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax, rbx
        """
    elif e.data == "exp_reel":
        # TODO
        return f""
    elif e.data == "exp_im":
        # TODO
        return f""
    elif e.data == "exp_i":
        # TODO
        return f""
    elif e.data == "exp_j":
        # TODO
        return f""
    elif e.data == "exp_k":
        # TODO
        return f""
    else :
        return "Cas non traité"

def asm_com(c):
    if c.data == "assignation":
        # TODO
        E = asm_exp(c.children[1])
        return f"""
        {E}
        mov [{c.children[0].value}], rax        
        """
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
        # TODO : apparemment le print va être différent lui aussi
        E = asm_exp(c.children[0])
        return f"""
        {E}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """
    else :
        return "Cas non traité"

def asm_bcom(bc):
    return "".join([asm_com(c) for c in bc.children])

def asm_prg(p):
    # TODO : vérifier si le moule est identique
    f = open("moule.asm")
    moule = f.read()
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    E = asm_exp(p.children[2])
    moule = moule.replace("RETURN", E)
    # TODO : vérifier si la déclaration des variables ne change pas
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
    # TODO : l'initialisation va forcément changer
    s = ""
    for i in range(len(p.children[0].children)):
        v = p.children[0].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + { 8*(i+1)}]
        xor rax, rax
        call atoi
        mov [{v}], rax
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)    
    return moule


#### VARIABLES SET ####

def vars_exp(e):
    if e.data  == "exp_nombre":
        return set()
    elif e.data ==  "exp_var":
        return { e.children[0].value }
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    else:
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R

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

#ast = grammaire.parse("""
#    main(x,y,z){
#        c = 1 + 3i + 4j + 5k;
#        print(c.i)
#    }
#""")
#asm = asm_prg(ast)
#f = open("quat.asm", "w")
#f.write(asm)
#f.close()
