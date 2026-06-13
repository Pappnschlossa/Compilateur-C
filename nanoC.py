import lark

grammaire = lark.Lark("""
IDENTIFIER: /[a-zA-Z_][a-zA-Z_0-9]*/
OPBIN: /[+\-*\/<>]/
vars : (IDENTIFIER ",")* IDENTIFIER -> liste_vars
expression : IDENTIFIER -> variable
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
%ignore WS
""", start="main")

compteur = iter(range(1000000000))

def transform_exp(ast):
    
    if ast.data == "entier" or ast.data == "variable":
        return
    
    transform_exp(ast.children[0])
    transform_exp(ast.children[2])
    
    op = ast.children[1].value

    # simplification d'operation entre deux entiers
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

def asm_expression(ast, available=["rax", "rbx", "rcx", "rdx", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]):

    # optimisation de l'arbre
    transform_exp(ast)
    
    if ast.data == "variable":
        return f"mov {available[0]}, [{ast.children[0].value}]\n"
    if ast.data == "entier":
        return f"mov {available[0]}, {ast.children[0].value}\n"
    
    opbin = {"+" : "add", "-" : "sub", "*" : "imul"}
    op = opbin[ast.children[1].value]

    # dans le cas x + x, x - x or x * x
    if ast.children[0].data == "variable" and ast.children[2].data == "variable":
        if ast.children[0].children[0].value == ast.children[2].children[0].value:
            return f"mov {available[0]}, [{ast.children[0].children[0].value}]\n{op} {available[0]}, {available[0]}\n"
    
    # il ne reste plus assez de place dans les registres pour continuer la récursion
    if len(available) == 2:
        eg = asm_expression(ast.children[0], available)
        ed = asm_expression(ast.children[2], available)
        return f"{eg}push {available[0]}\n{ed}pop {available[1]}\n{op} {available[0]}, {available[1]}\n"

    eg = asm_expression(ast.children[0], available)
    ed = asm_expression(ast.children[2], available[1:])
    return f"{eg}{ed}{op} {available[0]}, {available[1]}\n"

def asm_commande(ast):
    if ast.data == "assignation":
        lhs = ast.children[0].value
        rhs = asm_expression(ast.children[1])
        return f"{rhs}mov [{lhs}], rax\n"
    if ast.data == "pass":
        return "nop\n"
    if ast.data == "print":
        exp = asm_expression(ast.children[0])
        return f"{exp}mov rdi, format\nmov rsi, rax\nxor rax, rax\ncall printf\n"
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
        return f"{test}\ncmp rax, 0\njz fin_{cpt}\n{cmd}\nfin_{cpt}:\n"

def asm_vars(ast):
    return "".join(f"mov rdi, [argv]\nadd rdi, {(i+1)*8}\ncall atoi\nmov [{ast.children[i].value}], rax\n" for i in range(len(ast.children)))

def asm_decls_vars(ast):
    return "\n".join(f"{ast.children[i].value}: dq 0" for i in range(len(ast.children)))

def asm_main(ast):
    decls = asm_decls_vars(ast.children[0])
    vs = asm_vars(ast.children[0])
    cmd = asm_commande(ast.children[1])
    ret = asm_expression(ast.children[2])
    squelette = open("squelette.asm").read()
    squelette = squelette.replace("DECL_VARS", decls)
    squelette = squelette.replace("INIT_VARS", vs)
    squelette = squelette.replace("COMMANDE", cmd)
    squelette = squelette.replace("RETURN", ret)
    return squelette