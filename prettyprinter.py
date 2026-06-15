import nanoC

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
LIGHTGREY = "\033[37m"
GREY = "\033[90m"

OPENPAR = f"{MAGENTA}({RESET}"
CLOSEPAR = f"{MAGENTA}){RESET}"
OPENBRA = f"{GREY}{{{RESET}"
CLOSEBRA = f"{GREY}}}{RESET}"

ENDL = f"{GREY};{RESET}\n"
INDENT = "    "

def pp_expression(ast):
    if ast.data == "variable":
        return ast.children[0].value
    if ast.data == "entier":
        return ast.children[0].value
    if ast.data == "flottant":
        return ast.children[0].value
    if ast.data == "struct_arg":
        return ast.children[0].value
    eg = f"{pp_expression(ast.children[0])}"
    op = ast.children[1].value
    ed = f"{pp_expression(ast.children[2])}"
    return f"{eg} {op} {ed}"

def pp_commande(ast, indent=1):
    tab = INDENT * indent
    if ast.data == "assignation":
        lhs = ast.children[0].value
        rhs = pp_expression(ast.children[1])
        return f"{tab}{lhs} = {rhs}{ENDL}"
    if ast.data == "struct_assign":
        lhs = ast.children[0].value
        struc = ast.children[1].value
        rhs = "".join(pp_commande(c) for c in ast.children[2].children)
        print("pretty test")
        print(rhs)
        return f"{tab}{lhs} = {struc}({rhs}){ENDL}"
    if ast.data == "pass":
        return f"{tab}pass{ENDL}"
    if ast.data == "print":
        return f"{tab}{BLUE}print{RESET}{OPENPAR}{pp_expression(ast.children[0])}{CLOSEPAR}{ENDL}"
    if ast.data == "sequence":
        cg = pp_commande(ast.children[0], indent)
        cd = pp_commande(ast.children[1], indent)
        return f"{cg}{cd}"
    if ast.data in ("if", "while"):
        cg = pp_expression(ast.children[0])
        cd = pp_commande(ast.children[1], indent + 1)
        return f"{tab}{MAGENTA}{ast.data}{RESET} {OPENPAR}{cg}{CLOSEPAR} {OPENBRA}\n{cd}{tab}{CLOSEBRA}\n"

def pp_vars(ast):
    return ", ".join((v.value for v in ast.children))

def pp_struct(ast):
    var = "".join((f"{INDENT}{e.children[0].value}{ENDL}" for e in ast.children[1:]))
    return f"{MAGENTA}struct{RESET} {BLUE}{ast.children[0].value}{RESET} {OPENBRA}\n{var}{CLOSEBRA}{ENDL}"

def pp_structs(ast): # structs has n structures as children
    return "".join((f"{pp_struct(s)}\n" for s in ast.children))

def pp_main(ast):
    vs = pp_vars(ast.children[0])
    cmd = pp_commande(ast.children[1])
    ret = pp_expression(ast.children[2])
    return f"{BLUE}main{RESET}{OPENPAR}{vs}{CLOSEPAR} {OPENBRA}\n{cmd}{INDENT}{MAGENTA}return{RESET} {OPENPAR}{ret}{CLOSEPAR}{ENDL}{CLOSEBRA}"

def pp_statement(ast):
    return f"{pp_structs(ast.children[0])} {pp_main(ast.children[1])}"