"""The generic logic cells (flow/circuit/devices.py) as sg13g2_stdcell cells (1.2 V); every cell of
the library is in ``primitives.prim_dicts.stdcells``."""

import hdl21 as h

from .pdk_data import IhpLogicParams
from .primitives.prim_dicts import stdcells

# generic logic cell and drive band -> sg13g2 cell (pins: Y output, A / B inputs, VDD, VSS)
_LOGIC = {
    ("inverter", 1): stdcells["sg13g2_inv_1"],
    ("inverter", 4): stdcells["sg13g2_inv_4"],
    ("inverter", 8): stdcells["sg13g2_inv_8"],
    ("nor2", 2): stdcells["sg13g2_nor2_2"],
    ("nand2", 1): stdcells["sg13g2_nand2_2"],  # nand2_1 is too narrow for three pin accesses
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
