"""Local HDL21 and VLSIR contract tests for IHP SG13G2."""

from io import StringIO

import hdl21 as h
import pytest

from pdk import ihp130
from pdk.ihp130 import site
from pdk.ihp130.primitives.prim_dicts import default_xtor_size, xtors

_MOS_VARIANTS = tuple(
    (mos_type, mos_vth, mos_family, module.name) for (_, mos_type, mos_vth, mos_family), module in xtors.items()
)


def test_supply_metadata() -> None:
    rails = ihp130.Install.SUPPLY_RAILS
    assert rails["VDD"]["nominal"] > 0.0
    assert ihp130.Install.supply_voltage(h.pdk.Corner.SLOW) == rails["VDD"]["min"]
    assert ihp130.Install.supply_voltage(h.pdk.Corner.TYP) == rails["VDD"]["nominal"]
    assert ihp130.Install.supply_voltage(h.pdk.Corner.FAST) == rails["VDD"]["max"]


@pytest.mark.parametrize(("mos_type", "mos_vth", "mos_family", "model_name"), _MOS_VARIANTS)
def test_compile_and_netlist_mos_variant(
    mos_type: h.MosType,
    mos_vth: h.MosVth,
    mos_family: h.MosFamily,
    model_name: str,
) -> None:
    @h.module
    class Dut:
        d, g, s, b = h.Signals(4)
        m = h.Mos(tp=mos_type, vth=mos_vth, family=mos_family, w=2, l=1)(d=d, g=g, s=s, b=b)

    ihp130.compile(Dut)
    call = Dut.m.of
    assert isinstance(call, h.ExternalModuleCall)
    assert call.module.name == model_name
    default_w, default_l = default_xtor_size[model_name]
    assert float(call.params.w) == pytest.approx(2 * float(default_w))
    assert float(call.params.l) == pytest.approx(float(default_l))

    for fmt in ("spice", "spectre"):
        output = StringIO()
        h.netlist(Dut, output, fmt=fmt)
        assert model_name in output.getvalue()


@pytest.mark.site_pdk
def test_site_files_exist() -> None:
    missing = [path for path in site.MODEL_FILES if not path.exists()]
    assert not missing, f"Missing IHP SG13G2 site files: {missing}"
