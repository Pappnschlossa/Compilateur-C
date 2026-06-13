import nanoC
import prettyprinter

if __name__ == "__main__":
    src = open("source.c").read()
    t = nanoC.grammaire.parse(src)
    print("\n\033[107m    Source                                              \033[0m\n")
    print(src)
    print("\n\033[107m    Pretty Print                                        \033[0m\n")
    print(prettyprinter.pp_main(t))
    print("\n\033[107m    Assembleur                                          \033[0m\n")
    print(nanoC.asm_statement(t))

    print(prettyprinter.pp_statement(t))
    with open("resultat.asm", "w") as f:
        f.write(nanoC.asm_statement(t))
    print("\n\033[107m    Retour                                              \033[0m\n")