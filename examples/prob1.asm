section text
add r1 r0 999
add r3 r0 r0
loop:
    mod r2 r1 3
    je r2 ok
    mod r2 r1 5
    je r2 ok
    sub r1 r1 1
    je r1 end
    jmp loop
ok:
    add r3 r3 r1
    sub r1 r1 1
    je r1 end
    jmp loop
end:
    out r3