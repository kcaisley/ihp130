# IHP SG13G2 for plain OpenROAD: the technology and the sg13g2_stdcell standard cells.
# A design script sources this first, then reads its own views, netlist and constraints.

set PLATFORM_DIR [file dirname [file normalize [info script]]]

read_lef $PLATFORM_DIR/sg13g2_tech.lef
read_lef $PLATFORM_DIR/lef/sg13g2_stdcell.lef
read_liberty $PLATFORM_DIR/lib/sg13g2_stdcell_typ_1p20V_25C.lib.gz  ;# typical; slow_1p08V_125C is slow
