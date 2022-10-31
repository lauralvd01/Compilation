import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER "\+" SIGNED_NUMBER "i\+" SIGNED_NUMBER "j\+" SIGNED_NUMBER "k"     -> exp_nombre
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
%ignore WS
""",start="prg")

op = {'+' : 'add', '-' : 'sub', '*' : 'mult'}
coordonnees = [0,0,0,0] # VALIDE pour n'enregistrer qu'1 SEUL quaternion seulement !
## TODO : revoir l'exemple du prof pour voir comment il fait pour sauvegarder des valeurs !

###
# def asm_exp(e):
#    if e.data == "exp_nombre":
#        return f"mov rax, {e.children[0].value}\n"
#    elif e.data == "exp_var":
#        return f"mov rax, [{e.children[0].value}]\n"
#    elif e.data == "exp_par":
#        return asm_exp(e.children[0])
#    else:
#        E1 = asm_exp(e.children[0])
#        E2 = asm_exp(e.children[2])
#        return f"""
#        {E2}
#        push rax
#        {E1}
#        pop rbx
#        {op[e.children[1].value]} rax, rbx
#        """
###

def pp_exp(e):
    global coordonnees
    if e.data == "exp_nombre":
        return f"{e.children[0].value} + {e.children[1].value}i + {e.children[2].value}j + {e.children[3].value}k"
    elif e.data == "exp_var":
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "exp_opbin":
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
    elif e.data == "exp_reel":
        return f"{coordonnees[0]}"
    elif e.data == "exp_im":
        return f"{coordonnees[1]}i + {coordonnees[2]}j + {coordonnees[3]}k"
    elif e.data == "exp_i":
        return f"{coordonnees[1]}i"
    elif e.data == "exp_j":
        return f"{coordonnees[2]}j"
    elif e.data == "exp_k":
        return f"{coordonnees[3]}k"
    else:
        return "Cas non autorisé actuellement"

#def vars_exp(e):
#    if e.data  == "exp_nombre":
#        return set()
#    elif e.data ==  "exp_var":
#        return { e.children[0].value }
#    elif e.data == "exp_par":
#        return vars_exp(e.children[0])
#    else:
#        L = vars_exp(e.children[0])
#        R = vars_exp(e.children[2])
#        return L | R

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

#def asm_com(c):
#    if c.data == "assignation":
#        E = asm_exp(c.children[1])
#        return f"""
#        {E}
#        mov [{c.children[0].value}], rax        
#        """
#    elif c.data == "if":
#        E = asm_exp(c.children[0])
#        C = asm_bcom(c.children[1])
#        n = next()
#        return f"""
#        {E}
#        cmp rax, 0
#        jz fin{n}
#        {C}
#fin{n} : nop
#"""
#    elif c.data == "while":
#        E = asm_exp(c.children[0])
#        C = asm_bcom(c.children[1])
#        n = next()
#        return f"""
#        debut{n} : {E}
#        cmp rax, 0
#        jz fin{n}
#        {C}
#        jmp debut{n}
#fin{n} : nop
#"""
#    elif c.data == "print":
#        E = asm_exp(c.children[0])
#        return f"""
#        {E}
#        mov rdi, fmt
#        mov rsi, rax
#        call printf
#        """

def pp_com(c):
    if c.data == "assignation":
        return f"{c.children[0].value} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        x = f"\n{pp_bcom(c.children[1])}"
        return f"if ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "while":
        x = f"\n{pp_bcom(c.children[1])}"
        return f"while ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"


#def vars_com(c):
#    if c.data == "assignation":
#        R = vars_exp(c.children[1])
#        return {c.children[0].value} | R
#    elif c.data in {"if", "while"}:
#        B = vars_bcom(c.children[1])
#        E = vars_exp(c.children[0]) 
#        return E | B
#    elif c.data == "print":
#        return vars_exp(c.children[0])

#def asm_bcom(bc):
#    return "".join([asm_com(c) for c in bc.children])

def pp_bcom(bc):
    return "\n".join([pp_com(c) for c in bc.children])

#def vars_bcom(bc):
#    S = set()
#    for c in bc.children:
#        S = S | vars_com(c)
#    return S

def pp_var_list(vl):
    return ", ".join([t.value for t in vl.children])

#def asm_prg(p):
#    f = open("moule.asm")
#    moule = f.read()
#    C = asm_bcom(p.children[1])
#    moule = moule.replace("BODY", C)
#    E = asm_exp(p.children[2])
#    moule = moule.replace("RETURN", E)
#    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
#    moule = moule.replace("DECL_VARS", D)
#    s = ""
#    for i in range(len(p.children[0].children)):
#        v = p.children[0].children[i].value
#        e = f"""
#        mov rbx, [argv]
#        mov rdi, [rbx + { 8*(i+1)}]
#        xor rax, rax
#        call atoi
#        mov [{v}], rax
#        """
#        s = s + e
#    moule = moule.replace("INIT_VARS", s)    
#    return moule

#def vars_prg(p):
#    L = set([t.value for t in p.children[0].children])
#    C = vars_bcom(p.children[1])
#    R = vars_exp(p.children[2])
#    return L | C | R

def pp_prg(p):
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main( %s ) { %s return(%s);\n}" % (L, C, R)


ast = grammaire.parse("""
    main(x,y,z){
        c = 1 + 3i + 4j + 5k;
        print(c.i)
    }
""")
#asm = asm_prg(ast)
#f = open("quat.asm", "w")
#f.write(asm)
#f.close()
