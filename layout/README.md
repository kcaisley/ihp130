# Layout (IHP SG13G2)

The PDK's layout description, shared by every generator and layout tool: the layers, the metal and
via rules, and the values of the stems row cells (cells one standard-cell row tall, sg13g2_stdcell), so
analog blocks place like digital logic and share rows, rails and wells with the library. The
generators themselves know no PDK: the stems engine and the cIcCreator, laygo and ALIGN drivers
are in `flow/layout/`, and everything they generate goes to the superproject's `build/layout/`.

| Module | Contents |
| --- | --- |
| `tech.py` | layers (`LAYERS`), DBU and grid, metal and via rules (`RULES`), and the row profile and rule values the stems engine draws with |
| `paths.py` | library and access-point locations |
| `netlists/` | the PDK's hand-written test netlists (`mos_inv.sp`, the single-device test) |

## Row profile (the stems row cells)

nm, cell frame R0 (VSS at the bottom), from `tech.py`:

| | NMOS | PMOS |
| --- | --- | --- |
| diffusion (`OD_LIMIT`) | 480..2720 | 1060..3300 |
| gate bar and its M2 track (`GATE_TRACK`) | 2940 | 840 |
| S/D M2 tracks (`SD_TRACKS`) | 840 1260 1680 2100 | 2940 2520 2100 1680 |

Row height `H` = 3780, M2 track pitch `PITCH` = 420, placement grid `XPITCH` = 480, rail
half width `RAIL` = 220, widest finger `W_MAX` = 2240; MOS models sg13_lv_nmos / sg13_lv_pmos.

## Notes

- The laygo server works in this PDK's layer numbers and names; `flow/layout/laygo/post.py` maps them back to the target PDK.
- MOS fingers are `ng` in the models.
