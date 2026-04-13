# Protocol Specification

Messages are null-terminated (\0)

## Commands

READ
→ returns: x,y,z,q1,q2,q3,q4

MOVEJ,x,y,z,q1,q2,q3,q4
→ returns: OK / NOK_PARSE

MOVEL,x,y,z,q1,q2,q3,q4
→ returns: OK / NOK_PARSE

IOONN
→ returns: OK_prijemalo_zaprto

IOOFF
→ returns: OK_prijemalo_odprto