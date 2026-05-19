extern printf, atoi
section .data
argv: dq 0
format: db "%lld\n", 0
x: dq 0
y: dq 0
global main
section .text
main:
push rbp
mov rbp, rsp
mov [argv], rsi
mov rdi, [argv]
add rdi, 8
call atoi
mov [x], rax
mov rdi, [argv]
add rdi, 16
call atoi
mov [y], rax

debut_0: mov rax, [x]
cmp rax, 0
jz fin_0
mov rax, 1
push rax
mov rax, [x]
pop rbx
sub rax, rbx

mov [x], rax
mov rax, 1
push rax
mov rax, [y]
pop rbx
add rax, rbx

mov [y], rax
jmp debut_0
fin_0:
mov rax, [y]

mov rdi, format
mov rsi, rax
xor rax, rax
call printf

mov rax, [y]

pop rbp
ret