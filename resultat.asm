extern printf, atoi
section .data
argv: dq 0
format_int:   db "%d", 10, 0
format_float: db "%f", 10, 0

x_type: dq 0
x: dq 0
__float_0: dq 1.1
__float_1: dq 5.1
global main
section .text
main:
push rbp
mov rbp, rsp
mov [argv], rsi

mov rbx, 1
movsd xmm0, [__float_1]

mov [x_type], rbx
cmp rbx, 1
je variable_est_flottant_0
mov [x], rax
jmp fin_0
variable_est_flottant_0:
movsd [x], xmm0
fin_0:    
mov rbx, 0
mov rax, 1

mov [x_type], rbx
cmp rbx, 1
je variable_est_flottant_1
mov [x], rax
jmp fin_1
variable_est_flottant_1:
movsd [x], xmm0
fin_1:    
mov rbx, [x_type]
cmp rbx, 1
je variable_est_flottant_3
mov rax, [x]
jmp fin_3
variable_est_flottant_3:
movsd xmm0, [x]
fin_3:

cmp rbx, 1
push rbx
je gauche_est_flottant_2

mov rdx, rax
jmp fin_gauche_2

gauche_est_flottant_2:
movsd xmm2, xmm0

fin_gauche_2:
mov rbx, 1
movsd xmm0, [__float_0]


cmp rbx, 1
je droit_est_flottant_2

pop rbx
cmp rbx, 1
je gauche_flottant_droit_entier_2

; les deux sont entiers:
mov r8, rax
add rdx, r8
mov rax, rdx
mov rbx, 0
jmp fin_2

gauche_flottant_droit_entier_2:
cvtsi2sd xmm3, rax
addsd xmm2, xmm3
movsd xmm0, xmm2
mov rbx, 1
jmp fin_2

droit_est_flottant_2:
pop rbx
cmp rbx, 1
je les_deux_flottants_2

; gauche entier droit flottant:
cvtsi2sd xmm2, rdx
addsd xmm2, xmm0
movsd xmm0, xmm2
mov rbx, 1
jmp fin_2

les_deux_flottants_2:
addsd xmm2, xmm0
movsd xmm0, xmm2
mov rbx, 1
jmp fin_2

fin_2:

mov [x_type], rbx
cmp rbx, 1
je variable_est_flottant_4
mov [x], rax
jmp fin_4
variable_est_flottant_4:
movsd [x], xmm0
fin_4:    
mov rbx, [x_type]
cmp rbx, 1
je variable_est_flottant_6
mov rax, [x]
jmp fin_6
variable_est_flottant_6:
movsd xmm0, [x]
fin_6:

cmp rbx, 1
je print_flottant_5
mov rdi, format_int
mov rsi, rax
xor rax, rax
jmp fin_print_5
print_flottant_5:
mov rdi, format_float
mov rax, 1
fin_print_5:
call printf

mov rbx, [x_type]
cmp rbx, 1
je variable_est_flottant_7
mov rax, [x]
jmp fin_7
variable_est_flottant_7:
movsd xmm0, [x]
fin_7:

pop rbp
ret