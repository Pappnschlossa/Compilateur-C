#!/bin/bash
# run debut
python3.12 main.py
nasm -f elf64 resultat.asm
gcc -no-pie resultat.o -o resultat
./resultat > output.txt
