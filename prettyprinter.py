import nanoC

def pp_expression(ast):
    if ast.data in ("variable", "entier"):
        return ast.children[0].value
    eg = f"{pp_expression(ast.children[0])}"
    op = ast.children[1].value
    ed = f"{pp_expression(ast.children[2])}"
    return f"{eg} {op} {ed}"

def pp_commande(ast, indent=1):
    tab = "    " * indent
    if ast.data == "assignation":
        lhs = ast.children[0].value
        rhs = pp_expression(ast.children[1])
        return f"{tab}{lhs} = {rhs};\n"
    if ast.data == "pass":
        return f"{tab}pass;\n"
    if ast.data == "print":
        return f"{tab}print({pp_expression(ast.children[0])});\n"
    if ast.data == "sequence":
        cg = pp_commande(ast.children[0], indent)
        cd = pp_commande(ast.children[1], indent)
        return f"{cg}{cd}"
    if ast.data in ("if", "while"):
        cg = pp_expression(ast.children[0])
        cd = pp_commande(ast.children[1], indent + 1)
        return f"{tab}{ast.data} ({cg}) {{\n{cd}{tab}}}\n"

def pp_vars(ast):
    return ", ".join( (v.value for v in ast.children))

def pp_main(ast):
    vs = pp_vars(ast.children[0])
    cmd = pp_commande(ast.children[1])
    ret = pp_expression(ast.children[2])
    return f"main({vs}) {{\n{cmd}    return ({ret});\n}}"