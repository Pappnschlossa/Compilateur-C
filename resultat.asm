extern printf, atoi
section .data
argv: dq 0
format_int:   db "%d", 10, 0
format_float: db "%f", 10, 0

x_type: dq 0
x: dq 0
__float_0: dq 5.1
__float_1: dq 1.9000000000000001

global main
section .text
main:
push rbp
mov rbp, rsp
mov [argv], rsi



mov rbx, 1
movsd xmm0, [__float_0]

mov [x_type], rbx
cmp rbx, 1
je variable_est_flottant_6
mov [x], rax
jmp fin_6
variable_est_flottant_6:
movsd [x], xmm0
fin_6:    

mov rbx, 0
mov rax, 1

mov [x_type], rbx
cmp rbx, 1
je variable_est_flottant_7
mov [x], rax
jmp fin_7
variable_est_flottant_7:
movsd [x], xmm0
fin_7:    

mov rbx, 1
movsd xmm0, [__float_1]

mov [x_type], rbx
cmp rbx, 1
je variable_est_flottant_8
mov [x], rax
jmp fin_8
variable_est_flottant_8:
movsd [x], xmm0
fin_8:    

mov rbx, [x_type]
cmp rbx, 1
je variable_est_flottant_10
mov rax, [x]
jmp fin_10
variable_est_flottant_10:
movsd xmm0, [x]
fin_10:

cmp rbx, 1
je print_flottant_9
mov rdi, format_int
mov rsi, rax
xor rax, rax
jmp fin_print_9
print_flottant_9:
mov rdi, format_float
mov rax, 1
fin_print_9:
call printf


mov rbx, [x_type]
cmp rbx, 1
je variable_est_flottant_11
mov rax, [x]
jmp fin_11
variable_est_flottant_11:
movsd xmm0, [x]
fin_11:


pop rbp
ret