from pydub import AudioSegment
from pydub.playback import play
import lark
INT = 0
FLOAT = 1
grammaire = lark.Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
OPBIN: /[+\-*\/<>]/
vars : (IDENTIFIER ",")* IDENTIFIER -> liste_vars
     |                              -> liste_vide
expression : IDENTIFIER -> variable
           | SIGNED_FLOAT -> flottant
           | SIGNED_NUMBER -> entier
           | expression OPBIN expression -> binaire
commande : IDENTIFIER "=" expression ";" -> assignation
| commande* commande -> sequence
| "pass" -> pass
| "print" "(" expression ")" ";" -> print
| "if" "(" expression ")" "{" commande "}" -> if
| "while" "(" expression ")" "{" commande "}" -> while
main: "main" "(" vars ")" "{" commande "return" "(" expression ")" ";" "}"
%import common.WS
%import common.SIGNED_NUMBER
%import common.SIGNED_FLOAT
%ignore WS
""", start="main")

compteur = iter(range(1000000000))

def asm_expression(ast, available_registers = None, available_float_registers = None):
    if available_registers == None:
        available_registers = ["rdx", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"] # On garde rax, rbx, et rcx pour d'autres buts
    if available_float_registers == None:
        available_float_registers = ["xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7"] # On garde xmm0 et xmm1
    if ast.data == "variable":
        i = next(compteur)
        return f"""mov rbx, [{ast.children[0].value}_type]
cmp rbx, {FLOAT}
je variable_est_flottant_{i}
mov rax, [{ast.children[0].value}]
jmp fin_{i}
variable_est_flottant_{i}:
movsd xmm0, [{ast.children[0].value}]
fin_{i}:
"""
    if ast.data == "entier":
        return f"mov rbx, {INT}\nmov rax, {ast.children[0].value}\n"
    if ast.data == "flottant":
        label = float_labels[ast.children[0].value]
        return f"mov rbx, {FLOAT}\nmovsd xmm0, [{label}]\n"
    else: # (ast.data == "binaire")
        opbin = {'+' : 'add', '-' : 'sub', '*' : 'imul'}
        floatopbin = {'+' : 'addsd', '-' : 'subsd', '*' : 'mulsd'}
        if len(available_float_registers) < 2:
            float_reg_left = "xmm1"
            float_reg_right = available_float_registers[0]
        else:
            float_reg_left = available_float_registers[0]
            float_reg_right = available_float_registers[1]
        if len(available_registers) < 2:
            i = next(compteur)
            eg = f"{asm_expression(ast.children[0], available_registers, available_float_registers)}"
            op = ast.children[1].value
            ed = f"{asm_expression(ast.children[2], available_registers, available_float_registers)}"
            return f"""{eg}
cmp rbx, {FLOAT}
push rbx
je gauche_est_flottant_{i}

push rax
jmp fin_gauche_{i}

gauche_est_flottant_{i}:
sub rsp, 8 
movsd [rsp], xmm0

fin_gauche_{i}:
{ed}

cmp rbx, {FLOAT}
je droit_est_flottant_{i}

pop rbx
cmp rbx, {FLOAT}
je gauche_flottant_droit_entier_{i}

; les deux sont entiers:
pop rcx
{opbin[op]} rcx, rax
mov rax, rcx
mov rbx, {INT}
jmp fin_{i}

gauche_flottant_droit_entier_{i}:
movsd xmm0, [rsp]
add rsp, 8
cvtsi2sd xmm1, rax
{floatopbin[op]} xmm0, xmm1
mov rbx, {FLOAT}
jmp fin_{i}

droit_est_flottant_{i}:
pop rbx
cmp rbx, {FLOAT}
je les_deux_flottants_{i}

; gauche entier droit flottant:
pop rcx
cvtsi2sd xmm1, rcx
{floatopbin[op]} xmm0, xmm1
mov rbx, {FLOAT}
jmp fin_{i}

les_deux_flottants_{i}:
movsd xmm1, [rsp]
add rsp, 8 
{floatopbin[op]} xmm1, xmm0
movsd xmm0, xmm1
mov rbx, {FLOAT}
jmp fin_{i}

fin_{i}:
"""
        else:
            i = next(compteur)
            eg = f"{asm_expression(ast.children[0], available_registers, available_float_registers)}"
            op = ast.children[1].value
            ed = f"{asm_expression(ast.children[2], available_registers[1:], available_float_registers)}"
            reg_left = available_registers[0]
            reg_right = available_registers[1]
            return f"""{eg}
cmp rbx, {FLOAT}
push rbx
je gauche_est_flottant_{i}

mov {reg_left}, rax
jmp fin_gauche_{i}

gauche_est_flottant_{i}:
movsd {float_reg_left}, xmm0

fin_gauche_{i}:
{ed}

cmp rbx, {FLOAT}
je droit_est_flottant_{i}

pop rbx
cmp rbx, {FLOAT}
je gauche_flottant_droit_entier_{i}

; les deux sont entiers:
mov {reg_right}, rax
{opbin[op]} {reg_left}, {reg_right}
mov rax, {reg_left}
mov rbx, {INT}
jmp fin_{i}

gauche_flottant_droit_entier_{i}:
cvtsi2sd {float_reg_right}, rax
{floatopbin[op]} {float_reg_left}, {float_reg_right}
movsd xmm0, {float_reg_left}
mov rbx, {FLOAT}
jmp fin_{i}

droit_est_flottant_{i}:
pop rbx
cmp rbx, {FLOAT}
je les_deux_flottants_{i}

; gauche entier droit flottant:
cvtsi2sd {float_reg_left}, {reg_left}
{floatopbin[op]} {float_reg_left}, xmm0
movsd xmm0, {float_reg_left}
mov rbx, {FLOAT}
jmp fin_{i}

les_deux_flottants_{i}:
{floatopbin[op]} {float_reg_left}, xmm0
movsd xmm0, {float_reg_left}
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
        return f"{cg}{cd}"
    if ast.data == "while":
        test = asm_expression(ast.children[0])
        cmd = asm_commande(ast.children[1])
        cpt = next(compteur)
        return f"""debut_{cpt}: {test}cmp rax, 0
jz fin_{cpt}
{cmd}jmp debut_{cpt}
fin_{cpt}:
"""
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

if __name__ == "__main__":
    src = open("source.c").read()
    t = grammaire.parse(src)
    with open("resultat.asm", "w") as f:
        f.write(asm_main(t))
    play(AudioSegment.from_wav("song.wav"))