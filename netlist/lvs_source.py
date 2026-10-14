"""LVS source for a row design in SG13G2: the netlist (MOS lines as written, w the total width,
ng the fingers), plus the sg13g2_stdcell subcircuits of the standard cells it uses.

    uv run python pdk/ihp130/netlist/lvs_source.py build/layout/netlists/ihp130/comp_frida1_stdcells.sp out.cdl
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "layout"))
from paths import STD_SPICE


def subckts(names: set[str]) -> list[str]:
    out, keep = [], False
    for line in STD_SPICE.read_text().splitlines():
        f = line.split()
        if f and f[0].lower() == ".subckt":
            keep = f[1] in names
        if keep:
            out.append(line)
        if f and f[0].lower() == ".ends":
            keep = False
    return out


def lvs_source(src: str | Path, dst: str | Path) -> None:
    """Write the LVS source for the netlist ``src`` to ``dst``."""

    lines, cells = [], set()
    for line in Path(src).read_text().splitlines():
        f = line.split()
        if f and f[0][0] in "Xx":
            cells.add(f[-1])
        lines.append(line)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text("\n".join(subckts(cells) + lines) + "\n")


if __name__ == "__main__":
    lvs_source(*sys.argv[1:3])
