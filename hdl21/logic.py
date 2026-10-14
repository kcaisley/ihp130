"""The comparator generator's generic logic cells (flow/comp/subckt.py) as SG13G2 standard cells."""

import hdl21 as h

from .digital_cells import stdcells
from .pdk_data import IhpLogicParams

# generic logic cell and drive band -> sg13g2 cell (pins: Y output, A / B inputs, VDD, VSS)
_LOGIC = {
    ("inverter", 1): stdcells.inv_1,
    ("inverter", 4): stdcells.inv_4,
    ("inverter", 8): stdcells.inv_8,
    ("nor2", 2): stdcells.nor2_2,
    ("nand2", 1): stdcells.nand2_2,  # nand2_1 is too narrow for three pin accesses
}
_WRAPPERS: dict[tuple[str, int], h.Module] = {}


def logic_cell(kind: str, params) -> h.Module:
    """A generic inverter, NOR2 or NAND2 (inputs A, B; output Y) as its sg13g2 cell."""

    key = (kind, params.drive)
    if key in _WRAPPERS:
        return _WRAPPERS[key]
    cell = _LOGIC.get(key)
    if cell is None:
        raise ValueError(f"no sg13g2 cell for a {kind} of drive {params.drive}")
    wrapper = h.Module(name=f"ihp130_{kind}_d{params.drive}")
    wrapper.A, wrapper.Y = h.Input(), h.Output()
    wrapper.VDD, wrapper.VSS = h.Inout(), h.Inout()
    pins = {"A": wrapper.A, "Y": wrapper.Y, "VDD": wrapper.VDD, "VSS": wrapper.VSS}
    if kind != "inverter":
        wrapper.B = h.Input()
        pins["B"] = wrapper.B
    wrapper.add(cell(IhpLogicParams())(**pins), name="cell")
    _WRAPPERS[key] = wrapper
    return wrapper
