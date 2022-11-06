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

variables = {}


### ASM ###
def asm_exp(e):
    if e.data == "exp_int":
        return f"mov rax, {e.children[0].value}\n"
    if e.data == "exp_float":
        return f"mov rax, __float64__({e.children[0].value})\n"
    elif e.data == "exp_var":
        return f"mov rax, [{variables[e.children[0].value][1]}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    else:
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax, rbx
        """


def asm_com(c):
    if c.data == "assignation":
        # get the name of the variable
        v = c.children[0].value

        # get the type of the variable
        type = getType(c.children[1])

        # get the asm assignation
        E = asm_exp(c.children[1])

        # the variable do exist

        if type == variables[v][0]:
            # it is the same type as before
            # we just have to
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

    # we write the body of the assembly
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)

    # we return the variable
    E = asm_exp(p.children[2])
    moule = moule.replace("RETURN", E)

    # pop all the variables
    a = ""
    for i in range(cpt-1):
        a += "pop rbx\n"
    moule = moule.replace("END", a)

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
    else:
        return "undefined"


ast = grammaire.parse(""" main(y){
        
        a = 1;
        a=8.45;
        y=7;
        g=3;
        a=6;
        

 return (a);
 }

""")
asm = asm_prg(ast)
print("variable à la fin ", variables)
# print(asm)
f = open("ouf.asm", "w")
f.write(asm)
f.close()
