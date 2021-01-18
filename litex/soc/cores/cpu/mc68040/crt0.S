/*
 * Interrupt vector.
 */
.global _start
_start:

.long _fstack
.long _crt0

/*
 * Reset handler, branched to from the vector.
 */
_crt0:
  nop
  nop

  move.w #0x2700, %sr

  move.l #_fdata_rom, %a0
  move.l #_fdata, %a1
  move.l #_edata, %a2
  cmp.l %a1, %a2
  beq.s 2f
1:
  move.l (%a0)+, (%a1)+
  cmp.l %a1, %a2
  bne.s 1b
2:

  move.l #_fbss, %a0
  move.l #_ebss, %a1
  cmp.l %a0, %a1
  beq.s 2f
1:
  move.l #0, (%a0)+
  cmp.l %a0, %a1
  bne.s 1b
2:

  /* transparent translation */
  move.l #0x8200C040, %d0
  movec.l %d0, %dtt0
  movec.l %d0, %itt0

  /* enable cache */
  nop
  cinva %bc
  nop

  move.l #0x80008000, %d0
  movec.l %d0, %cacr

  /* jump to main */
  bsr main

1:
  /* loop forever */
  jsr 1b
