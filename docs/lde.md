# Layout-Dependent Effects (LDE): IHP SG13G2

- The low-voltage core devices `sg13_lv_nmos` and `sg13_lv_pmos` are subcircuit wrappers around
  **PSP 103.6** model cards (`sg13g2_lv_nmos_psp`, `sg13g2_lv_pmos_psp`; `*_psp_rf` with
  `pspnqs103va` when `rfmode=1`).
- The wrappers take `w`, `l`, `ng` (fingers), `m`, `as/ad/ps/pd`, `trise`, `rfmode` and
  `pre_layout`, but **no `sa`, `sb` or `sc` instance parameters**: LOD and WPE cannot be passed in.
- The model cards switch LOD and WPE off: `kvtho = kuo = kvsat = 0` (with their length and width
  scaling terms), and `web = wec = kvthoweo = kuoweo = 0`. `saref`, `sbref`, `scref` are left at
  1 um and have no effect. Edge-FET (`swedge = 0`) is off too.
- PSE, OSE, MBE and CESL are not modeled.
- **Junction areas and perimeters**: with `as = 0` (the schematic default) the wrapper computes
  `as/ad/ps/pd` from `w`, `ng` and the diffusion lengths `z1 = 0.34 um` (outer) and
  `z2 = 0.38 um` (shared), with different formulas for odd and even `ng`. Given values are used
  as they are (an extractor must then account for `ng` itself).
- **Gate resistance and RF parasitics** follow `rfmode` (default `0`): `rgo = rfmode * 40`,
  `rshg = rfmode * 3`, NQS (`swnqs = rfmode * 5`), bulk and well resistances
  (`rbulko`, `rwello`) and junction resistances (`rjunso`, `rjundo`). With `rfmode = 0` all are
  zero; there is no `rgflag`, `ccoflag` or `rcoflag`.
- `pre_layout` (default `1`) is declared on the wrappers but not used by the low-voltage MOS
  equations.
- The open KLayout LVS (`libs.tech/klayout/tech/lvs`) extracts `w`, `l`, `ng` and the junction
  geometry, nothing for LOD or WPE.
- Interconnect parasitics are not in the device models; they come from extraction.

FRIDA's layouts therefore need no LDE-driven sizing in IHP: matching relies on the usual
symmetry (common centroid, dummies) rather than on the model.

### Sources

- [sg13g2_moslv_mod.lib](file:///home/kcaisley/Documents/libs/IHP-Open-PDK/ihp-sg13g2/libs.tech/ngspice/models/sg13g2_moslv_mod.lib#L66) — the `sg13_lv_nmos` / `sg13_lv_pmos` wrappers
- [sg13g2_moslv_parm.lib](file:///home/kcaisley/Documents/libs/IHP-Open-PDK/ihp-sg13g2/libs.tech/ngspice/models/sg13g2_moslv_parm.lib#L61) — the PSP 103.6 model cards

## Flags

| Effect | Type | Flag | Setting | Default |
|--------|------|------|---------|---------|
| LOD / STI stress | LDE | — | No `sa`/`sb`; `kvtho = kuo = kvsat = 0` | Not modeled |
| Poly Spacing Effect (PSE) | LDE | — | — | Not modeled |
| OD Spacing Effect (OSE) | LDE | — | — | Not modeled |
| Well Proximity Effect (WPE) | LDE | — | No `sc`; `web = wec = kvthoweo = 0` | Not modeled |
| Metal Boundary Effect (MBE) | LDE | — | — | Not modeled |
| Contact Etch Stop Liner (CESL) | LDE | — | — | Not modeled |
| Junction area / perimeter | Pre-layout | `as = 0` | Computed from `w`, `ng`, `z1`, `z2` | Computed |
| Poly gate resistance (RG) | Pre-layout | `rfmode` | `rgo = rfmode * 40`, `rshg = rfmode * 3` | **0** (off) |
| NQS, bulk, well and junction resistances | Pre-layout | `rfmode` | `swnqs`, `rbulko`, `rwello`, `rjunso`, `rjundo` scale with `rfmode` | **0** (off) |
