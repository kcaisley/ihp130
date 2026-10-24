"""The generic logic cells (flow/circuit/devices.py) and clock XOR (flow/capdriver/subckt.py) as SG13G2 standard cells."""

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


# the clock XOR's drive bands: SG13G2 has one XOR (xor2_1); bands 2 and 4 add the library's
# non-inverting buffer of that drive after it
_XOR_BUFFERS = {1: None, 2: stdcells.buf_2, 4: stdcells.buf_4}
_XOR_WRAPPERS: dict[int, h.Module] = {}


def clock_xor(params) -> h.Module:
    """The capacitor driver's clock XOR (Y = A XOR B) of a drive band as SG13G2 cells."""

    band = params.drive_band
    if band in _XOR_WRAPPERS:
        return _XOR_WRAPPERS[band]
    if band not in _XOR_BUFFERS:
        raise ValueError(f"no sg13g2 clock XOR of drive band {band}")
    wrapper = h.Module(name=f"ihp130_clock_xor_b{band}")
    wrapper.A, wrapper.B, wrapper.Y = h.Input(), h.Input(), h.Output()
    wrapper.VDD, wrapper.VSS = h.Inout(), h.Inout()
    buffer = _XOR_BUFFERS[band]
    xor_out = wrapper.Y if buffer is None else wrapper.add(h.Signal(name="xor_out"))
    supplies = {"VDD": wrapper.VDD, "VSS": wrapper.VSS}
    wrapper.add(stdcells.xor2_1(IhpLogicParams())(A=wrapper.A, B=wrapper.B, X=xor_out, **supplies), name="xor")
    if buffer is not None:
        wrapper.add(buffer(IhpLogicParams())(A=xor_out, X=wrapper.Y, **supplies), name="buf")
    _XOR_WRAPPERS[band] = wrapper
    return wrapper
