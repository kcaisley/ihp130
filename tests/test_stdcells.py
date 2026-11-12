"""Compile-only standard-cell contracts; no foundry models or simulator required."""

from pathlib import Path

import hdl21 as h
import pytest

from pdk import ihp130 as pdk
from pdk.ihp130.hdl21 import cells, site
from pdk.ihp130.hdl21.pdk_logic import IhpWalker as Walker
from pdk.ihp130.hdl21.primitives.prim_dicts import stdcells
from pdk.ihp130.hdl21.stdcells import _LOGIC, logic_cell


def test_unrelated_external_call_unchanged():
    for domain, name in (("generic", "other"), ("other", "clock_xor")):
        call = h.ExternalModule(domain=domain, name=name, port_list=[], paramtype=h.HasNoParams)()
        assert Walker().visit_external_module_call(call) is call


def test_stdcell_include_is_separate():
    include = site.install.include_stdcell()
    assert isinstance(include, h.sim.Include)
    assert include.path == site.STDCELL_PATH
    assert include.path.is_file()  # the package's own copy, present without any site install
    assert include.path not in site.MODEL_FILES
    assert isinstance(site.install.include(h.pdk.Corner.TYP), h.sim.Lib)
    assert pdk.Install.supply_voltage(h.pdk.Corner.TYP) == 1.2
    custom = pdk.Install(pdk_path=Path("/models"), stdcell_path=Path("/cells/library.sp"))
    assert custom.include_stdcell().path == Path("/cells/library.sp")
    with pytest.raises(ValueError, match="standard-cell library path"):
        pdk.Install(pdk_path=Path("/models")).include_stdcell()
    # ngspice reads the open PDK's models and cells, a second install
    with pytest.raises(ValueError, match="open PDK"):
        pdk.Install(pdk_path=Path("/models")).simulation_includes(h.pdk.Corner.TYP, "ngspice")


def test_library_cells_match_the_library():
    assert set(stdcells) == set(cells.CELLS)
    for name, (pins, _) in cells.CELLS.items():
        assert [port.name for port in stdcells[name].port_list] == list(pins)


@pytest.mark.parametrize(("kind", "drive"), sorted(_LOGIC))
def test_logic_cells_are_library_cells(kind: str, drive: int):
    params = type("Params", (), {"drive": drive})()
    wrapper = logic_cell(kind, params)
    assert logic_cell(kind, params) is wrapper
    (inst,) = wrapper.instances.values()
    assert inst.of.module is stdcells[inst.of.module.name]
    assert set(wrapper.ports) == ({"A", "Y", "VDD", "VSS"} | (set() if kind == "inverter" else {"B"}))
    with pytest.raises(ValueError, match="no sg13g2 cell"):
        logic_cell(kind, type("Params", (), {"drive": 99})())
