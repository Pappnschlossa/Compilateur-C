#!/bin/bash
# run debut

source venv/bin/activate
python3 main.py
nasm -f elf64 resultat.asm
gcc -no-pie resultat.o -o resultat
./resultat > output.txt
cat output.txt