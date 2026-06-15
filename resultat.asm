extern printf, atoi
section .data
argv: dq 0
format_int:   db "%d", 10, 0
format_float: db "%f", 10, 0

s : dq 0
s_type : dq 0
mov qword [s_type], 2
s.b : dq 0
s.b_type : dq 0
mov qword [s.b_type], 2
z_type: dq 0
z: dq 0
x_type: dq 0
x: dq 0
__float_0: dq 1.1

global main
section .text
main:
push rbp
mov rbp, rsp
mov [argv], rsi




mov rbx, 0
mov rax, 1

mov [s + 0 + 8], rbx
cmp rbx, 1
je variable_est_flottant_0
mov [s + 0], rax
jmp fin_0
variable_est_flottant_0:
movsd [s + 0], xmm0
fin_0:    


mov rbx, [s + 0 + 8]
cmp rbx, 1
je variable_est_flottant_2
mov rax, [s + 0]
jmp fin_2
variable_est_flottant_2:
movsd xmm0, [s + 0]
fin_2:

cmp rbx, 1
push rbx
je gauche_est_flottant_1

jmp fin_gauche_1

gauche_est_flottant_1:

fin_gauche_1:
mov rbx, 0
mov rcx, 2


cmp rbx, 1
je droit_est_flottant_1

pop rbx
cmp rbx, 1
je gauche_flottant_droit_entier_1

; les deux sont entiers:
add rax, rcx
mov rbx, 0
jmp fin_1

gauche_flottant_droit_entier_1:
cvtsi2sd xmm2, rcx
addsd xmm0, xmm2
mov rbx, 1
jmp fin_1

droit_est_flottant_1:
pop rbx
cmp rbx, 1
je les_deux_flottants_1

; gauche entier droit flottant:
cvtsi2sd xmm0, rax
addsd xmm0, xmm2
mov rbx, 1
jmp fin_1

les_deux_flottants_1:
addsd xmm0, xmm2
mov rbx, 1
jmp fin_1

fin_1:

mov [x_type], rbx
cmp rbx, 1
je variable_est_flottant_3
mov [x], rax
jmp fin_3
variable_est_flottant_3:
movsd [x], xmm0
fin_3:    


mov rbx, 1
movsd xmm0, [__float_0]

mov [s.b + 0 + 8], rbx
cmp rbx, 1
je variable_est_flottant_4
mov [s.b + 0], rax
jmp fin_4
variable_est_flottant_4:
movsd [s.b + 0], xmm0
fin_4:    

mov rbx, 0
mov rax, 42

mov [z_type], rbx
cmp rbx, 1
je variable_est_flottant_5
mov [z], rax
jmp fin_5
variable_est_flottant_5:
movsd [z], xmm0
fin_5:    


mov rbx, [s.b + 0 + 8]
cmp rbx, 1
je variable_est_flottant_8
mov rax, [s.b + 0]
jmp fin_8
variable_est_flottant_8:
movsd xmm0, [s.b + 0]
fin_8:

cmp rbx, 1
push rbx
je gauche_est_flottant_7

jmp fin_gauche_7

gauche_est_flottant_7:

fin_gauche_7:

mov rbx, [z_type]
cmp rbx, 1
je variable_est_flottant_9
mov rcx, [z]
jmp fin_9
variable_est_flottant_9:
movsd xmm2, [z]
fin_9:


cmp rbx, 1
je droit_est_flottant_7

pop rbx
cmp rbx, 1
je gauche_flottant_droit_entier_7

; les deux sont entiers:
add rax, rcx
mov rbx, 0
jmp fin_7

gauche_flottant_droit_entier_7:
cvtsi2sd xmm2, rcx
addsd xmm0, xmm2
mov rbx, 1
jmp fin_7

droit_est_flottant_7:
pop rbx
cmp rbx, 1
je les_deux_flottants_7

; gauche entier droit flottant:
cvtsi2sd xmm0, rax
addsd xmm0, xmm2
mov rbx, 1
jmp fin_7

les_deux_flottants_7:
addsd xmm0, xmm2
mov rbx, 1
jmp fin_7

fin_7:

cmp rbx, 1
je print_flottant_6
mov rdi, format_int
mov rsi, rax
xor rax, rax
jmp fin_print_6
print_flottant_6:
mov rdi, format_float
mov rax, 1
fin_print_6:
call printf


mov rbx, 0
mov rax, 0


pop rbp
ret