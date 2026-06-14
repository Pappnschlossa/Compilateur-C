# from pydub import AudioSegment
# from pydub.playback import play
import lark

INT = 0
FLOAT = 1
STRUCT = 2

OPBIN_INT = {"+" : "add", "-" : "sub", "*" : "imul"}
OPBIN_FLOAT = {'+' : 'addsd', '-' : 'subsd', '*' : 'mulsd'}

grammaire = lark.Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
OPBIN: /[+\-*\/<>]/

struct : ("typedef struct " IDENTIFIER "{" (definition ";")* "};") -> struct
structs : struct* -> liste_struct
vars : (IDENTIFIER ",")* IDENTIFIER -> liste_vars
     | -> liste_vide
expression : IDENTIFIER -> variable
           | SIGNED_FLOAT -> flottant
           | SIGNED_NUMBER -> entier
           | expression OPBIN expression -> binaire
definition : IDENTIFIER -> define
commande : IDENTIFIER "=" expression ";" -> assignation
         | commande* commande -> sequence
         | "pass" -> pass
         | "print" "(" expression ")" ";" -> print
         | "if" "(" expression ")" "{" commande "}" -> if
         | "while" "(" expression ")" "{" commande "}" -> while
main : "main" "(" vars ")" "{" commande "return" "(" expression ")" ";" "}"
statement : structs main

%import common.WS
%import common.SIGNED_NUMBER
%import common.SIGNED_FLOAT
%ignore WS
""", start="statement")

compteur = iter(range(1000000000))

def transform_expression(ast):
    
    if ast.data == "entier" or ast.data == "flottant" or ast.data == "variable":
        return
    
    transform_expression(ast.children[0])
    transform_expression(ast.children[2])
    
    op = ast.children[1].value

    # simplification d'opération entre deux entiers
    if ast.children[0].data == "entier" and ast.children[2].data == "entier":
        value1 = int(ast.children[0].children[0].value)
        value2 = int(ast.children[2].children[0].value)
        result = 0
        if op == "+":
            result = value1 + value2
        if op == "-":
            result = value1 - value2
        if op == "*":
            result = value1 * value2
        ast.data = "entier"
        ast.children = [lark.Token("SIGNED_NUMBER", str(result))]
        return
    
    # simplification d'opération entre deux flottants ou entier et flottant
    if (ast.children[0].data == "flottant" or ast.children[0].data == "entier") and (ast.children[2].data == "flottant" or ast.children[2].data == "entier"):
        value1 = float(ast.children[0].children[0].value)
        value2 = float(ast.children[2].children[0].value)
        result = 0.0
        if op == "+":
            result = value1 + value2
        if op == "-":
            result = value1 - value2
        if op == "*":
            result = value1 * value2
        ast.data = "flottant"
        ast.children = [lark.Token("SIGNED_FLOAT", str(result))]
        return
    
    # simplification de la multiplication par 0
    if op == "*" and ast.children[0].data == "entier" and ast.children[0].children[0] == "0":
        ast.data = "entier"
        ast.children = [lark.Token("SIGNED_NUMBER", "0")]
        return
    if op == "*" and ast.children[2].data == "entier" and ast.children[2].children[0] == "0":
        ast.data = "entier"
        ast.children = [lark.Token("SIGNED_NUMBER", "0")]
        return
    
    # simplification de la multiplication par 1
    if op == "*" and ast.children[0].data == "entier" and ast.children[0].children[0] == "1":
        ast.data = ast.children[2].data
        ast.children = ast.children[2].children
        return
    if op == "*" and ast.children[2].data == "entier" and ast.children[2].children[0] == "1":
        ast.data = ast.children[0].data
        ast.children = ast.children[0].children
        return
    
    # simplification de l'addition avec 0
    if op == "+" and ast.children[0].data == "entier" and ast.children[0].children[0] == "0":
        ast.data = ast.children[2].data
        ast.children = ast.children[2].children
        return
    if op == "+" and ast.children[2].data == "entier" and ast.children[2].children[0] == "0":
        ast.data = ast.children[0].data
        ast.children = ast.children[0].children
        return
    
def transform_commande(ast):
    if ast.data == "assignation":
        transform_expression(ast.children[1])
    if ast.data == "print":
        transform_expression(ast.children[0])
    if ast.data == "sequence":
        transform_commande(ast.children[0])
        transform_commande(ast.children[1])
    if ast.data == "if" or ast.data == "while":
        transform_expression(ast.children[0])
        transform_commande(ast.children[1])

def transform_main(ast):
    transform_commande(ast.children[1])
    transform_expression(ast.children[2])

def asm_expression(ast, available_int=["rax", "rcx", "rdx", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"], available_float=["xmm0", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"]):
    
    if ast.data == "variable":
        i = next(compteur)
        return f"""mov rbx, [{ast.children[0].value}_type]
cmp rbx, {FLOAT}
je variable_est_flottant_{i}
mov {available_int[0]}, [{ast.children[0].value}]
jmp fin_{i}
variable_est_flottant_{i}:
movsd {available_float[0]}, [{ast.children[0].value}]
fin_{i}:
"""
    if ast.data == "entier":
        return f"mov rbx, {INT}\nmov {available_int[0]}, {ast.children[0].value}\n"
    
    if ast.data == "flottant":
        label = float_labels[ast.children[0].value]
        return f"mov rbx, {FLOAT}\nmovsd {available_float[0]}, [{label}]\n"
    
    int_op = OPBIN_INT[ast.children[1].value]
    float_op = OPBIN_FLOAT[ast.children[1].value]

    # dans le cas x + x, x - x ou x * x
    if ast.children[0].data == "variable" and ast.children[2].data == "variable":
        if ast.children[0].children[0].value == ast.children[2].children[0].value:
            return f"mov {available_int[0]}, [{ast.children[0].children[0].value}]\n{op} {available_int[0]}, {available_int[0]}\n"
    
    # il ne reste plus assez de place dans les registres pour continuer la récursion
    if len(available_int) == 2 and len(available_float) == 2:
        i = next(compteur)
        eg = asm_expression(ast.children[0], available_int, available_float)
        ed = asm_expression(ast.children[2], available_int, available_float)
        return f"""{eg}
cmp rbx, {FLOAT}
push rbx
je gauche_est_flottant_{i}

push {available_int[0]}
jmp fin_gauche_{i}

gauche_est_flottant_{i}:
sub rsp, 8
movsd [rsp], {available_float[0]}

fin_gauche_{i}:
{ed}

cmp rbx, {FLOAT}
je droit_est_flottant_{i}

pop rbx
cmp rbx, {FLOAT}
je gauche_flottant_droit_entier_{i}

; les deux sont entiers:
pop {available_int[1]}
{int_op} {available_int[0]}, {available_int[1]}
mov rbx, {INT}
jmp fin_{i}

gauche_flottant_droit_entier_{i}:
movsd {available_float[0]}, [rsp]
add rsp, 8
cvtsi2sd {available_float[1]}, {available_int[0]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

droit_est_flottant_{i}:
pop rbx
cmp rbx, {FLOAT}
je les_deux_flottants_{i}

; gauche entier droit flottant:
pop {available_int[0]}
cvtsi2sd {available_float[0]}, {available_int[0]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

les_deux_flottants_{i}:
movsd {available_float[1]}, [rsp]
add rsp, 8
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

fin_{i}:
"""
    elif len(available_int) > 2 and len(available_float) == 2:
        i = next(compteur)
        eg = asm_expression(ast.children[0], available_int, available_float)
        ed = asm_expression(ast.children[2], available_int[1:], available_float)
        return f"""{eg}
cmp rbx, {FLOAT}
push rbx
je gauche_est_flottant_{i}

jmp fin_gauche_{i}

gauche_est_flottant_{i}:
sub rsp, 8
movsd [rsp], {available_float[0]}

fin_gauche_{i}:
{ed}

cmp rbx, {FLOAT}
je droit_est_flottant_{i}

pop rbx
cmp rbx, {FLOAT}
je gauche_flottant_droit_entier_{i}

; les deux sont entiers:
{int_op} {available_int[0]}, {available_int[1]}
mov rbx, {INT}
jmp fin_{i}

gauche_flottant_droit_entier_{i}:
movsd {available_float[0]}, [rsp]
add rsp, 8
cvtsi2sd {available_float[1]}, {available_int[1]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

droit_est_flottant_{i}:
pop rbx
cmp rbx, {FLOAT}
je les_deux_flottants_{i}

; gauche entier droit flottant:
cvtsi2sd {available_float[0]}, {available_int[0]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

les_deux_flottants_{i}:
movsd {available_float[1]}, [rsp]
add rsp, 8
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

fin_{i}:
"""
    elif len(available_int) == 2 and len(available_float) > 2:
        i = next(compteur)
        eg = asm_expression(ast.children[0], available_int, available_float)
        ed = asm_expression(ast.children[2], available_int, available_float[1:])
        return f"""{eg}
cmp rbx, {FLOAT}
push rbx
je gauche_est_flottant_{i}

push {available_int[0]}
jmp fin_gauche_{i}

gauche_est_flottant_{i}:

fin_gauche_{i}:
{ed}

cmp rbx, {FLOAT}
je droit_est_flottant_{i}

pop rbx
cmp rbx, {FLOAT}
je gauche_flottant_droit_entier_{i}

; les deux sont entiers:
pop {available_int[1]}
{int_op} {available_int[0]}, {available_int[1]}
mov rbx, {INT}
jmp fin_{i}

gauche_flottant_droit_entier_{i}:
cvtsi2sd {available_float[1]}, {available_int[0]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

droit_est_flottant_{i}:
pop rbx
cmp rbx, {FLOAT}
je les_deux_flottants_{i}

; gauche entier droit flottant:
pop {available_int[0]}
cvtsi2sd {available_float[0]}, {available_int[0]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

les_deux_flottants_{i}:
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

fin_{i}:
"""
    #len(available_int) > 2 and len(available_float) > 2
    i = next(compteur)
    eg = f"{asm_expression(ast.children[0], available_int, available_float)}"
    op = ast.children[1].value
    ed = f"{asm_expression(ast.children[2], available_int[1:], available_float[1:])}"
    return f"""{eg}
cmp rbx, {FLOAT}
push rbx
je gauche_est_flottant_{i}

jmp fin_gauche_{i}

gauche_est_flottant_{i}:

fin_gauche_{i}:
{ed}

cmp rbx, {FLOAT}
je droit_est_flottant_{i}

pop rbx
cmp rbx, {FLOAT}
je gauche_flottant_droit_entier_{i}

; les deux sont entiers:
{int_op} {available_int[0]}, {available_int[1]}
mov rbx, {INT}
jmp fin_{i}

gauche_flottant_droit_entier_{i}:
cvtsi2sd {available_float[1]}, {available_int[1]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

droit_est_flottant_{i}:
pop rbx
cmp rbx, {FLOAT}
je les_deux_flottants_{i}

; gauche entier droit flottant:
cvtsi2sd {available_float[0]}, {available_int[0]}
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

les_deux_flottants_{i}:
{float_op} {available_float[0]}, {available_float[1]}
mov rbx, {FLOAT}
jmp fin_{i}

fin_{i}:
"""

def asm_commande(ast):
    if ast.data == "assignation":
        lhs = ast.children[0].value
        rhs = asm_expression(ast.children[1])
        i = next(compteur)
        return f"""{rhs}
mov [{lhs}_type], rbx
cmp rbx, {FLOAT}
je variable_est_flottant_{i}
mov [{lhs}], rax
jmp fin_{i}
variable_est_flottant_{i}:
movsd [{lhs}], xmm0
fin_{i}:    
"""
    if ast.data == "pass":
        return "nop\n"
    if ast.data == "print":
        i = next(compteur)
        return f"""{asm_expression(ast.children[0])}
cmp rbx, {FLOAT}
je print_flottant_{i}
mov rdi, format_int
mov rsi, rax
xor rax, rax
jmp fin_print_{i}
print_flottant_{i}:
mov rdi, format_float
mov rax, 1
fin_print_{i}:
call printf
"""
    if ast.data == "sequence":
        cg = asm_commande(ast.children[0])
        cd = asm_commande(ast.children[1])
        return f"{cg}\n{cd}"
    if ast.data == "while":
        test = asm_expression(ast.children[0])
        cmd = asm_commande(ast.children[1])
        cpt = next(compteur)
        return f"debut_{cpt}: {test}cmp rax, 0\njz fin_{cpt}\n{cmd}jmp debut_{cpt}\nfin_{cpt}:\n"
    if ast.data == "if":
        test = asm_expression(ast.children[0])
        cmd = asm_commande(ast.children[1])
        cpt = next(compteur)
        return f"""{test}
cmp rax, 0
jz fin_{cpt}
{cmd}
fin_{cpt}:
"""

def asm_vars(ast):
    if ast.data == "liste_vide": return ""
    else:
        return "".join(
f"""mov rdi, [argv]
add rdi, {(i+1)*8}
call atoi
mov [{ast.children[i].value}], rax
""" for i in range(len(ast.children)))

def asm_decls_vars(ast, V, F):
    params = {ast.children[i].value for i in range(len(ast.children))}
    V_local = V - params

    global float_labels
    float_labels = {v: f"__float_{i}" for i, v in enumerate(F)}

    if ast.data == "liste_vide": first_part = ""
    else: first_part = "\n".join(f"{ast.children[i].value}_type: dq 0\n{ast.children[i].value}: dq 0"
                     for i in range(len(ast.children)))
    return first_part + "\n" + "\n".join(f"{v}_type: dq 0\n{v}: dq 0" for v in V_local) + "\n" + "\n".join(f"{float_labels[f]}: dq {f}" for f in F)

def asm_main(ast):
    V = collecter_vars(ast.children[1])
    F = collecter_flottants(ast.children[1]).union(collecter_flottants(ast.children[2]))
    decls = asm_decls_vars(ast.children[0], V, F)
    vs = asm_vars(ast.children[0])
    cmd = asm_commande(ast.children[1])
    ret = asm_expression(ast.children[2])
    squelette = open("squelette.asm").read()
    squelette = squelette.replace("DECL_VARS", decls)
    squelette = squelette.replace("INIT_VARS", vs)
    squelette = squelette.replace("COMMANDE", cmd)
    squelette = squelette.replace("RETURN", ret)
    return squelette

def collecter_vars(ast, V = None):
    if V == None:
        V = set()
    if ast.data == "assignation":
        V.add(ast.children[0].value)
        return V
    if ast.data == "sequence":
        return collecter_vars(ast.children[1], collecter_vars(ast.children[0], V))
    if ast.data in ("if", "while"):
        return collecter_vars(ast.children[1], V)
    return V

def collecter_flottants(ast, V = None):
    if V == None:
        V = set()
    if ast.data == "flottant":
        V.add(ast.children[0].value)
        return V
    if ast.data == "assignation":
        return collecter_flottants(ast.children[1], V)
    if ast.data == "print":
        return collecter_flottants(ast.children[0], V)
    if ast.data == "binaire":
        collecter_flottants(ast.children[0], V)
        return collecter_flottants(ast.children[2], V)
    if ast.data == "sequence":
        return collecter_flottants(ast.children[1], collecter_flottants(ast.children[0], V))
    if ast.data in ("if", "while"):
        return collecter_flottants(ast.children[1], collecter_flottants(ast.children[0], V))
    return V

def asm_struct(ast):
    for i in range(len(ast.children)):
        # ajouter dict avec tous les arguments de la struct
        x = 1
    return ""

def asm_statement(ast):
    transform_main(ast.children[1])
    structs = asm_struct(ast.children[0])
    main = asm_main(ast.children[1])
    return f"{structs}{main}"

if __name__ == "__main__":
    src = open("source.c").read()
    t = grammaire.parse(src)
    with open("resultat.asm", "w") as f:
        f.write(asm_statement(t))