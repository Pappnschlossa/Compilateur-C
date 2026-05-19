import nanoC
import prettyprinter

if __name__ == "__main__":
    src = open("source.c").read()
    t = nanoC.grammaire.parse(src)
    # print(asm_main(t))
    print(prettyprinter.pp_main(t))
    with open("resultat.asm", "w") as f:
        f.write(nanoC.asm_main(t))