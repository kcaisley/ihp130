"""SG13G2's LVS source rules, on the netlist's data (``flow.circuit.netlists``' LVS context, run
in a process bound to the kit): each MOS as compiled (w its total width, ng its fingers), the sg13g2_stdcell
subcircuits of the standard cells it calls.
"""

from __future__ import annotations


def _subckts(text: str, names: set[str]) -> list[str]:
    out, keep = [], False
    for line in text.splitlines():
        f = line.split()
        if f and f[0].lower() == ".subckt":
            keep = f[1] in names
        if keep:
            out.append(line)
        if f and f[0].lower() == ".ends":
            keep = False
    return out


def library(cells: set[str], devices: set[str]) -> str:
    """The library text the source calls: the standard cells' subcircuits (sg13g2_stdcell)."""
    from paths import STD_SPICE

    return "\n".join(_subckts(STD_SPICE.read_text(), cells))
