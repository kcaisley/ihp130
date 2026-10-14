.subckt mos_inv in out vdd vss
Mn out in vss vss sg13_lv_nmos w=2100n l=1690n ng=2 m=1
Mp out in vdd vdd sg13_lv_pmos w=2100n l=1690n ng=2 m=1
.ends mos_inv
