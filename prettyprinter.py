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

ENDL = f"{GREY};{RESET}"
INDENT = "    "

def pp_expression(ast):
    if ast.data == "variable":
        return ast.children[0].value
    if ast.data == "entier":
        return ast.children[0].value
    if ast.data == "flottant":
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
        return f"{tab}{lhs} = {rhs}{ENDL}\n"
    if ast.data == "pass":
        return f"{tab}pass{ENDL}\n"
    if ast.data == "print":
        return f"{tab}{BLUE}print{RESET}{OPENPAR}{pp_expression(ast.children[0])}{CLOSEPAR}{ENDL}\n"
    if ast.data == "sequence":
        cg = pp_commande(ast.children[0], indent)
        cd = pp_commande(ast.children[1], indent)
        return f"{cg}{cd}"
    if ast.data in ("if", "while"):
        cg = pp_expression(ast.children[0])
        cd = pp_commande(ast.children[1], indent + 1)
        return f"{tab}{MAGENTA}{ast.data}{RESET} {OPENPAR}{cg}{CLOSEPAR} {OPENBRA}\n{cd}{tab}{CLOSEBRA}\n"

def pp_vars(ast):
    return ", ".join( (v.value for v in ast.children))

def pp_main(ast):
    vs = pp_vars(ast.children[0])
    cmd = pp_commande(ast.children[1])
    ret = pp_expression(ast.children[2])
    return f"{BLUE}main{RESET}{OPENPAR}{vs}{CLOSEPAR} {OPENBRA}\n{cmd}    {MAGENTA}return{RESET} {OPENPAR}{ret}{CLOSEPAR}{ENDL}\n{CLOSEBRA}"