import lark

grammaire = lark.Lark(r"""
exp : SIGNED_INT                 -> exp_int
| SIGNED_FLOAT                   -> exp_float
| IDENTIFIER                     -> exp_var
| exp OPBIN exp                  -> exp_opbin
| "(" exp ")"                    -> exp_par
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
%import common.SIGNED_INT
%import common.SIGNED_FLOAT
%ignore WS
""", start="prg")

op = {'+': 'add', '-': 'sub'}
op_float = {'+': 'fadd', '-': 'fsub', '*': 'fmul'}

variables = {}


### ASM ###
def asm_exp(e, id=None):
    # Id permet de récuperer le nom de la variable (qui n'est pas dans e)
    # pour avoir accès a l'adresse
    if e.data == "exp_int":
        return f"mov rax, {e.children[0].value}\n"
    if e.data == "exp_float":
        return f"""mov rax, __float64__({e.children[0].value})"""
    elif e.data == "exp_var":
        return f"mov rax, [{variables[id][1]}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0], id)
    elif e.data == "exp_opbin":
        type = getType(e.children[0])

        s = ""
        if type == "int":
            print("now", e.children[0].data)
            if e.children[0].data == "exp_var":
                E1 = asm_exp(e.children[0], e.children[0].children[0])
            else:
                E1 = asm_exp(e.children[0])

            if e.children[2].data == "exp_var":
                E2 = asm_exp(e.children[2], e.children[2].children[0])
            else:
                E2 = asm_exp(e.children[2])

            s += f"""
            {E2}
            push rax
            {E1}
            pop rbx
            {op[e.children[1].value]} rax, rbx\n
            """
        elif type == "float":
            # Calcule le résultat de l'opération binaire sur les float
            # et enregistre le résultat dans st(0)
            # --> calcule le float résultat de l'expression 2 et l'empile en st(0)
            # --> calcule le float résultat de l'expression 1 et l'empile en st(0)
            # --> E2 devient st(1)

            if e.children[0].data == "exp_var":
                E1 = asm_exp(e.children[0], e.children[0].children[0])
            else:
                E1 = asm_exp(e.children[0])

            if e.children[2].data == "exp_var":
                E2 = asm_exp(e.children[2], e.children[2].children[0])
            else:
                E2 = asm_exp(e.children[2])

            # --> calcule st0 = st0 op_float st1 donc le résultat s'enregistre en st(0)
            s += f"""
            {E2}
            push rax
            fld qword [rsp]
            {E1}
            push rax
            fld qword [rsp]
            {op_float[e.children[1].value]} st0, st1
            fstp qword [rsp]
            pop rax
            add rsp, 8
            """

        return s


def asm_com(c):

    if c.data == "assignation":

        # get the name of the variable
        v = c.children[0].value

        # get the type of the variable

        type = getType(c.children[1])

        # get the asm assignation
        if c.children[1].data == "exp_var":
            E = asm_exp(c.children[1], c.children[1].children[0])
        else:
            print("here", c.children[1])
            E = asm_exp(c.children[1])

        if type == variables[v][0]:
            # it is the same type as before
            # we just have to change the value
            return f"""
            {E}
            mov [{variables[v][1]}], rax
            """

        else:
            variables[v] = [type,  f"rbp - {cpt*8}"]
            increment()
            return f"""
            {E}
            push rax
            """

    elif c.data == "if":

        E = asm_exp(c.children[0], c.children[0].children[0])
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

        E = asm_exp(c.children[0], c.children[0].children[0])
        if c.children[0].children[0] in variables:
            type = variables[c.children[0].children[0]][0]
        else:
            type = getType(c.children[0])

        s = f""
        pushed = False

        if (8*(cpt-1)) % 16 != 0:
            print(True)
            s += f"push rax\n"
            pushed = True

        if type == "int":
            s += f"""
        {E}
        mov rdi, int_fmt
        mov rsi, rax
        call printf\n
        """

        if type == "float":
            s += f"""
        {E}
         movq xmm0, qword rax   ; floating point in str
        mov rdi, float_fmt              ; address of format string
        mov rax, 1                  ; 1 floating point argument to printf
        call printf\n"""
        if pushed:
            s += "pop rbx\n"

        return s


def asm_bcom(bc):
    return "".join([asm_com(c) for c in bc.children])


def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()

    # get the name of all the variables used
    variablespos = [v for v in vars_prg(p)]

    # we set their type as "int" and give the an adress to use
    global variables
    for i in range(len(variablespos)):
        variables[variablespos[i]] = ["int", f"rbp - {cpt*8}"]
        increment()
    print("variables à l'init ", variables)

    # we declare the variables
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)

    # we set the arguments of the main to init the variables
    s = ""
    for i in range(len(p.children[0].children)):
        adress = variables[f"{p.children[0].children[i]}"][1]
        v = p.children[0].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + { 8*(i+1)}]
        xor rax, rax
        call atoi
        mov [{adress}], rax 
        """
        s = s + e
    s += f"sub rsp, {8*(len(variables)-1)}"
    moule = moule.replace("INIT_VARS", s)

    # pop all the variables at the end of assembly code

    # we write the body of the assembly

    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)

    # we return the variable

    a = ""
    for i in range(cpt-1):

        a += "pop rbx\n"
    moule = moule.replace("END", a)

    E = asm_exp(p.children[2], p.children[2].children[0])
    moule = moule.replace("RETURN", E)

    return moule


### PRETTY PRINTER###
def pp_exp(e):
    if e.data in {"exp_int", "exp_var", "exp_float"}:
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    else:
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"


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


def pp_bcom(bc):

    return "\n".join([pp_com(c) for c in bc.children])


def pp_var_list(vl):
    return ", ".join([t.value for t in vl.children])


def pp_prg(p):
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main( %s ) { %s\n return(%s);\n}" % (L, C, R)


### VARIABLES###
def vars_exp(e):
    if e.data == "exp_int":
        return set()
    if e.data == "exp_float":
        return set()
    elif e.data == "exp_var":
        return {e.children[0].value}
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


### OTHER###

# used to define the adresses of the variables
cpt = 0


def increment():
    global cpt
    cpt += 1

    return cpt


#used in asm_com
index = 0


def next():
    global index
    index += 1
    return index


def getType(e):
    if e.data == "exp_int":
        return "int"
    elif e.data == "exp_float":
        return "float"
    elif e.data == "exp_opbin":
        return getType(e.children[0])
    elif e.data == "exp_var":
        print("children=", e.children[0])
        return variables[e.children[0]][0]

    else:
        return "int"


ast = grammaire.parse(""" main(y){ 
        x = 1.4;
        z = 4.5;
        x = x + 0.4 ; 
        print(x)
        print(z)
 return (y);
 }
""")
asm = asm_prg(ast)
print("variable à la fin ", variables)
# print(asm)
f = open("ouf.asm", "w")
f.write(asm)
f.close()
