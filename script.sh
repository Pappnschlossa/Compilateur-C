#!/bin/bash
# run debut
python3 nanoC.py
nasm -f elf64 resultat.asm
gcc -no-pie resultat.o -o resultat
./resultat
