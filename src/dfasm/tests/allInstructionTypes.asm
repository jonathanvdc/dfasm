  ; simple instructions
  clts
  nop
  clc
  
  ; unary instructions
  not eax
  neg [ebx]
  
  ; setCC instructions
  seto al
  setno bl
  
  ; binary instructions
  xchg ecx, [ecx]
  lea eax, [eax + eax * 2 + 1]
  
  ; ambiguous binary instructions
  add eax, ebx
  xor esi, esi
  cmp ecx, 20
  
  ; shift instructions
  sal [eax], 1
  sar [eax], 20
  shr edx, cl
  
  ; jump instructions
  jmp toet
  call toet

toet:
  ; conditional jump instructions
  ja next

next:
  ; push/pop instructions
  push eax
  push [eax]
  pop eax
  pop [eax]
  
  ; misc.
  mov ebx, 4
  mov [eax + eax - 6], -1234567
  
  int 33
  
  test ah, ah
  test ebx, 1024
  
  enter 5, 0
  
  imul ebx
  imul ebx, [esi + 3]
  imul ebx, ecx, 5
  
  ret