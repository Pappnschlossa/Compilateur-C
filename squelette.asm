extern printf, atoi
section .data
argv: dq 0
format_int:   db "%d", 10, 0
format_float: db "%f", 10, 0
DECL_VARS

global main
section .text
main:
push rbp
mov rbp, rsp
mov [argv], rsi

INIT_VARS

COMMANDE

RETURN

pop rbp
ret