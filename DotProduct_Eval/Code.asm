LS SR1 SR0 0 # Array size
LS SR2 SR0 1 # Vector size
LS SR3 SR0 2 # Dividing factor
LS SR6 SR0 3 # Final number of elements
LS SR7 SR0 4 # VDMEM Address for storing result

# Strip mined Dot product and accumulation - final result 64 elements.
LV VR0 SR0
MULVV VR2 VR0 VR0
ADDVV VR3 VR3 VR2
ADD SR0 SR0 SR2
SUB SR4 SR1 SR0
BGE SR4 SR2 -5
MTCL SR4
BLT SR0 SR1 -7

# Store final result of 64 elements
MTCL SR2
SV VR3 SR1
# Reducing 64 elements to 1 in loop.
SRL SR2 SR2 SR3
ADD SR5 SR2 SR1
MTCL SR2
LV VR4 SR1
LV VR5 SR5
ADDVV VR6 VR4 VR5
SV VR6 SR1
BGT SR2 SR6 -7
SV VR6 SR7

# End.
HALT