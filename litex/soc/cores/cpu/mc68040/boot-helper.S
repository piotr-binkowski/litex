.section    .text, "ax", @progbits
.global     boot_helper
boot_helper:
	jmp boot_helper
	
