import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                 -> exp_nombre
| IDENTIFIER                        -> exp_var
| exp OPBIN exp                     -> exp_opbin
| "(" exp ")"                       -> exp_par
| "[" exp "]"             -> exp_array_creation
| IDENTIFIER "[" exp "]"  -> exp_array_access 

com : IDENTIFIER "=" exp ";"                    -> assignation
| "if" "(" exp ")" "{" bcom "}"                 -> if
| "while" "(" exp ")" "{" bcom "}"              -> while
| "print" "(" exp ")"                           -> print
| IDENTIFIER "[" exp "]" "=" exp ";"            -> set_array_value


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

op = {'+' : 'add', '-' : 'sub'}

##### pretty printers ####

def pp_exp(e):
    if e.data in {"exp_nombre", "exp_var"}:
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "exp_opbin":
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
    elif e.data == "exp_array_creation":
        return f"[ {pp_exp(e.children[0])} ]"
    elif e.data == "exp_array_access" :
        return f"{e.children[0].value} [ {pp_exp(e.children[1])} ]"
    

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
    elif c.data == "set_array_value" :
        return f"{c.children[0].value} [ {pp_exp(c.children[1])} ] = {pp_exp(c.children[2])};"
    

def pp_bcom(bc):
    return "\n".join([pp_com(c) for c in bc.children])


def pp_prg(p):
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main( %s ) { %s \nreturn(%s);\n}" % (L, C, R)


def pp_var_list(vl):
    return ", ".join([t.value for t in vl.children])


##### variables #####


def vars_exp(e):
    if e.data  == "exp_nombre":
        return set()
    elif e.data ==  "exp_var":
        return { e.children[0].value }
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data =="exp_opbin":
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R
    elif e.data == "exp_array_creation":
        return vars_exp(e.children[0])
    elif e.data == "exp_array_access":
        index = vars_exp(e.children[1])
        return {e.children[0].value} | index


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
    elif c.data == "set_array_value":
        E = vars_exp(c.children[2])
        index = vars_exp(c.children[1])
        return {c.children[0].value} | index | E


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
    

##### assembly transformer #####

def asm_exp(e):
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var":
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    elif e.data == "exp_opbin":
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax, rbx
        """
    elif e.data == "exp_array_creation" :
        size = asm_exp(e.children[0])
        return f"""
        {size}
        mov rdi, rax
        add rdi, 1
        imul rdi, 8
        xor rax, rax
        call malloc
        
        mov rbx, rax
        {size}
        mov qword rbx, rax
        mov rax, rbx
        """
    elif e.data == "exp_array_access":
        id = e.children[0].value
        index = asm_exp(e.children[1])
        return f"""
        mov rdi, {id}
        {index}
        mov rbx, rax
        add rbx, 1
        imul rbx, 8
        add rdi, rbx
        mov rax, [rdi]
        """


cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_com(c):
    if c.data == "assignation":
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
        E = asm_exp(c.children[0])
        return f"""
        {E}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """
    elif c.data == "set_array_value" :
        id = c.children[0].value
        index = asm_exp(c.children[1])
        value = asm_exp(c.children[2])
        return f"""
        {value}
        mov rcx, rax
        mov rdi, {id}
        {index}
        mov rbx, rax
        add rbx, 1
        imul rbx, 8
        add rdi, rbx
        mov qword [rdi], rcx
        """


def asm_bcom(bc):
    return "".join([asm_com(c) for c in bc.children])


def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    E = asm_exp(p.children[2])
    moule = moule.replace("RETURN", E)
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
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



##### parsing #####

astCreation = grammaire.parse("""main(){
        tab = [0];
    return (tab);
}
""")

astCreationSize = grammaire.parse("""main(){
        tab = [15];
    return (tab[-1]);
}
""")

astAffectation = grammaire.parse("""main(){
    tab = [3];
    tab[0] = 10;
    tab[1] = 100;
    tab[2] = 1000;
    return (tab[1]);
}
""")


astAccess = grammaire.parse("""main(){
    tab = [3];
    tab[0] = 10;
    tab[1] = 100;
    tab[2] = 1000;
    somme = tab[0] + tab[1] + tab[2];
    return (somme);
}
""")

astAutoAccess = grammaire.parse("""main(){
        tab = [3];
        tab[0] = tab[-1];
        tab[1] = tab[0] + 1;
        tab[2] = tab[1] + 1;
    return (tab[2]);
}
""")

astMix = grammaire.parse("""main(){
        x = 5;
        tab = [11];
        tab[0] = x+2 ;
        print (tab[0])
        tab[1] = tab[0] + 1;
        y = tab[1]; 
    return (y);
}
""")

astWhile = grammaire.parse("""main(){
        x = 5;
        tab = [x];
        while(x){
            tab[x-1] = x;
            x = x - 1;
        }
    return (tab[2]);
}
""")


asm = asm_prg(astWhile)
# print(asm)
f = open("ouf.asm", "w")
f.write(asm)
f.close()

