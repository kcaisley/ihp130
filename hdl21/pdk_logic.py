"""
Hdl21 + IHP SG13G2 130nm BiCMOS PDK Modules and Transformations

Defines a set of `hdl21.ExternalModule`s comprising the essential devices of the
IHP SG13G2 130nm BiCMOS PDK, and an `hdl21pdk.netlist` method for converting
process-portable `hdl21.Primitive` elements into these modules.

The SG13G2 PDK features:
- Low-voltage (1.2V) and High-voltage (3.3V) CMOS transistors
- High-performance SiGe:C npn-HBTs with fT up to 350 GHz
- Various passive components (resistors, capacitors, varactors)
- ESD protection devices

Target devices for conversion from `hdl21.Primitive`:
- MOS transistors: sg13_lv_nmos, sg13_lv_pmos, sg13_hv_nmos, sg13_hv_pmos
- Bipolar: npn13G2 variants, pnpMPA
- Resistors: rsil, rhigh, rppd
- Capacitors: cap_cmim, cap_rfcmim
- Diodes: schottky_nbl1, ESD devices
"""

# Std-Lib Imports
from pathlib import Path
from typing import Any, ClassVar, Optional

# Hdl21 Imports
import hdl21 as h
from hdl21.pdk import PdkInstallation
from hdl21.primitives import (
    Bipolar,
    BipolarParams,
    Diode,
    DiodeParams,
    Mos,
    MosParams,
    PhysicalCapacitor,
    PhysicalCapacitorParams,
    PhysicalResistor,
    PhysicalResistorParams,
    ThreeTerminalCapacitor,
    ThreeTerminalResistor,
)

# PyPi Imports
from pydantic.dataclasses import dataclass

# Import relevant data from the PDK's data module
from .pdk_data import (
    IhpCapParams,
    IhpDiodeParams,
    IhpHbtParams,
    IhpMosHvParams,
    IhpMosParams,
    IhpPnpParams,
    IhpResParams,
)
from .primitives.prim_dicts import *

# The widest MOS finger each row-cell type fits (pdk/ihp130/layout/tech.py: W_MAX for the analog
# cells), in unit widths (default_xtor_size: 350 nm). Generators that place their devices in
# these cells read this through hdl21.pdk.default() and size every finger in whole units.
MOS_FINGER_UNITS = {"analog": 6, "logic_n": 2, "logic_p": 3}


@dataclass
class Install(PdkInstallation):
    """
    PDK Installation Data for the IHP SG13G2 process.

    This class represents site-specific PDK installation information, including paths to
    the PDK installation and SPICE model libraries. It provides methods to include the
    appropriate model files for different device types and process corners.

    Attributes:
        pdk_path: Path to the Cadence kit (IHP-SG13G2), whose models Spectre reads.
        model_lib: Relative path to the low-voltage MOS Spectre models.
        open_pdk_path: Path to an IHP-Open-PDK checkout, whose models and standard-cell netlist
            ngspice reads.
        osdi_path: Directory of the open PDK's Verilog-A models (psp103, psp103_nqs, r3_cmc,
            mosvar) compiled for ngspice (OpenVAF).
    """

    pdk_path: Path  # Path to PDK installation (IHP-SG13G2)
    model_lib: Path = Path("SG13G2_618_rev1.2.10/tech/SG13_MOS/library/spectreG2")
    open_pdk_path: Path | None = None
    osdi_path: Path | None = None

    LOCAL_SPICE_FILES: ClassVar[list[Path]] = [
        Path("SG13G2_618_rev1.2.10/tech/SG13_MOS/library/spectreG2/cornerMOSlv_psp.scs"),
        Path("SG13G2_618_rev1.2.10/tech/SG13_MOS/library/spectreG2/cornerMOShv_psp.scs"),
        Path("SG13G2_618_rev1.2.10/tech/SG13G2_HBT/VBIC/spectre/SG13G2_cornerBIP_vbic.scs"),
        Path("SG13G2_618_rev1.2.10/tech/SG13G2_PASSIVES/spectre/SG13_cornerRES.scs"),
        Path("SG13G2_618_rev1.2.10/tech/SG13G2_PASSIVES/spectre/SG13_cornerCAP.scs"),
        Path("SG13G2_618_rev1.2.10/tech/SG13G2_PASSIVES/spectre/sg13g2_dschottky_nbl1_corner.scs"),
        Path("SG13G2_618_rev1.2.10/tech/SG13_ESD/spectre/SG13_esd.lib"),
        Path("SG13G2_618_rev1.2.10/tech/SG13G2_PASSIVES/spectre/SG13_diodes.lib"),
    ]

    def include_stdcell(self) -> h.sim.Include:
        """Include the sg13g2 standard cells' SPICE (this package's copy, which the row cells draw
        from); transistor models must be included separately."""
        return h.sim.Include(path=Path(__file__).resolve().parents[1] / "openroad/sp/sg13g2_stdcell.sp")

    # what the site's model decks do not model, per simulator: a device, or "cells", and why
    # (pdk/test_spice.py)
    UNMODELED: ClassVar[dict[str, dict[str, str]]] = {
        "spectre": {
            name: "the kit has no HBT with its thermal node as a fifth pin (the open PDK's ngspice models do)"
            for name in ("npn13G2_5t", "npn13G2l_5t", "npn13G2v_5t")
        },
    }

    def simulation_includes(self, corner: h.pdk.Corner, simulator: str = "spectre", mismatch: bool = False) -> list:
        """What a simulation of this package's devices and standard cells includes, in order, for
        ``simulator`` ("spectre", or "ngspice" in HSPICE compatibility). Spectre: the kit's model
        libraries at ``corner`` (MOS, HBT, resistors, capacitors, diodes), the package's device
        names on the kit's, the standard cells. ngspice: the open PDK's compiled Verilog-A models,
        its model libraries at ``corner``, its standard-cell netlist. ``mismatch``: the same for
        Spectre, whose corner sections carry the mismatch statistics a Monte Carlo
        (``variations=mismatch``) varies; ngspice's are other sections (``mos_tt_mismatch``)."""

        if mismatch and simulator != "spectre":
            raise NotImplementedError("mismatch statistics: Spectre only")

        if simulator == "spectre":
            return [
                self.include_mos_lv(corner),
                self.include_mos_hv(corner),
                self.include_hbt(corner),
                self.include_res(corner),
                self.include_cap(corner),
                *self.include_diodes(corner),
                self.include_devices(),
                self.include_stdcell(),
            ]
        if simulator == "ngspice":
            return self.ngspice_includes(corner)
        raise ValueError(f"no {simulator} models for IHP SG13G2")

    def ngspice_includes(self, corner: h.pdk.Corner) -> list:
        """The open PDK's ngspice models at ``corner`` and its standard cells, after a control block
        that loads the compiled Verilog-A models (ngspice runs its ``pre_`` commands before it reads
        the circuit, whose PSP MOS, R3 resistors and varactors need them)."""

        if self.open_pdk_path is None or self.osdi_path is None:
            raise ValueError("IHP SG13G2's open PDK or its compiled Verilog-A models are not configured")
        mos = {h.pdk.Corner.TYP: "tt", h.pdk.Corner.FAST: "ff", h.pdk.Corner.SLOW: "ss"}[corner]
        case = {h.pdk.Corner.TYP: "typ", h.pdk.Corner.FAST: "bcs", h.pdk.Corner.SLOW: "wcs"}[corner]
        models = self.open_pdk_path / "ihp-sg13g2/libs.tech/ngspice/models"
        osdi = "".join(
            f"pre_osdi {self.osdi_path / name}.osdi\n" for name in ("psp103", "psp103_nqs", "r3_cmc", "mosvar")
        )
        return [
            h.sim.Literal(f".control\n{osdi}.endc"),
            h.sim.Lib(path=models / "cornerMOSlv.lib", section=f"mos_{mos}"),
            h.sim.Lib(path=models / "cornerMOShv.lib", section=f"mos_{mos}"),  # and the varactor
            h.sim.Lib(path=models / "cornerHBT.lib", section=f"hbt_{case}"),
            h.sim.Lib(path=models / "cornerRES.lib", section=f"res_{case}"),
            h.sim.Lib(path=models / "cornerCAP.lib", section=f"cap_{case}"),
            h.sim.Lib(path=models / "cornerDIO.lib", section=f"dio_{mos}"),  # ESD, Schottky, antennas
            # the cells' X lines name the MOS subcircuits (the package's copy has M lines)
            h.sim.Include(path=self.open_pdk_path / "ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice"),
        ]

    SUPPLY_RAILS: ClassVar[dict[str, dict[str, float]]] = {
        "VDD": {"nominal": 1.2, "min": 1.08, "max": 1.32},
        "VDDIO": {"nominal": 3.3, "min": 3.0, "max": 3.6},
        "VSS": {"nominal": 0.0, "min": 0.0, "max": 0.0},
    }

    @classmethod
    def supply_voltage(cls, corner: h.pdk.Corner, rail: str = "VDD") -> float:
        """Return rail voltage for the given process-voltage corner."""
        r = cls.SUPPLY_RAILS.get(rail.upper())
        if r is None:
            raise KeyError(f"Unknown rail '{rail}' for IHP SG13G2.")
        return {
            h.pdk.Corner.SLOW: r["min"],
            h.pdk.Corner.TYP: r["nominal"],
            h.pdk.Corner.FAST: r["max"],
        }[corner]

    def include_mos_lv(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the LV MOS model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for LV MOS devices.
        """
        corner_map: dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.model_lib / "cornerMOSlv_psp.scs",
            section=corner_map[corner],
        )

    def include_mos_hv(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the HV MOS model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for HV MOS devices.
        """
        corner_map: dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "tt",
            h.pdk.Corner.FAST: "ff",
            h.pdk.Corner.SLOW: "ss",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / self.model_lib / "cornerMOShv_psp.scs",
            section=corner_map[corner],
        )

    def include_hbt(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the HBT model include for the specified process corner: the kit's VBIC library,
        whose npn13G2 takes the package's parameters (Nx, Ny; the HICUM one has no Ny) and which
        alone has npn13G2l, npn13G2v and pnpMPA, as the open PDK's ngspice models do.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for HBT devices.
        """
        corner_map: dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "typ",
            h.pdk.Corner.FAST: "bcs",
            h.pdk.Corner.SLOW: "wcs",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / "SG13G2_618_rev1.2.10/tech/SG13G2_HBT/VBIC/spectre/SG13G2_cornerBIP_vbic.scs",
            section=corner_map[corner],
        )

    def include_res(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the resistor model include for the specified process corner.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for resistor devices.
        """
        corner_map: dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "typ",
            h.pdk.Corner.FAST: "bcs",
            h.pdk.Corner.SLOW: "wcs",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / "SG13G2_618_rev1.2.10/tech/SG13G2_PASSIVES/spectre/SG13_cornerRES.scs",
            section=corner_map[corner],
        )

    def include_cap(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the capacitor model include for the specified process corner. The kit's cap_cmim
        takes its capacitance from ``c`` (75.49 fF unless given), which the kit's CDF computes
        from w and l; the open PDK's (ngspice) computes it from w and l itself.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include for capacitor devices.
        """
        corner_map: dict[h.pdk.Corner, str] = {
            h.pdk.Corner.TYP: "typ",
            h.pdk.Corner.FAST: "bcs",
            h.pdk.Corner.SLOW: "wcs",
        }
        if not isinstance(corner, h.pdk.Corner) or corner not in corner_map:
            raise ValueError(f"Invalid corner {corner}")

        return h.sim.Lib(
            path=self.pdk_path / "SG13G2_618_rev1.2.10/tech/SG13G2_PASSIVES/spectre/SG13_cornerCAP.scs",
            section=corner_map[corner],
        )

    def include_diodes(self, corner: h.pdk.Corner) -> list:
        """The kit's diode models: the Schottky diode at ``corner``, the ESD diodes and the
        standard cells' antenna diodes (neither has corners)."""

        section = {h.pdk.Corner.TYP: "tt", h.pdk.Corner.FAST: "ff", h.pdk.Corner.SLOW: "ss"}[corner]
        tech = self.pdk_path / "SG13G2_618_rev1.2.10/tech"
        return [
            h.sim.Lib(path=tech / "SG13G2_PASSIVES/spectre/sg13g2_dschottky_nbl1_corner.scs", section=section),
            h.sim.Include(path=tech / "SG13_ESD/spectre/SG13_esd.lib"),
            h.sim.Include(path=tech / "SG13G2_PASSIVES/spectre/SG13_diodes.lib"),
        ]

    def include_devices(self) -> h.sim.Include:
        """Spectre definitions of the package's device names (the open PDK's) that the kit names
        otherwise, on the kit's devices; a simulation includes it after the model libraries."""
        return h.sim.Include(path=Path(__file__).resolve().parent / "spectre_devices.scs")

    def include(self, corner: h.pdk.Corner) -> h.sim.Lib:
        """
        Get the primary model include for the specified process corner.
        This returns the LV MOS corner by default for compatibility.

        Args:
            corner: The process corner (TYP, FAST, SLOW).

        Returns:
            h.sim.Lib: The model library include.
        """
        return self.include_mos_lv(corner)

    singleton: Optional["Install"] = None

    @classmethod
    def instance(cls) -> "Install":
        """Get the singleton Install instance."""
        if cls.singleton is None:
            raise ValueError("The Install instance has not been initialized yet.")
        return cls.singleton

    def __post_init__(self):
        if Install.singleton is not None:
            raise ValueError("The Install instance has already been initialized.")
        Install.singleton = self


class IhpWalker(h.HierarchyWalker):
    """
    Hierarchical Walker for IHP SG13G2 PDK.

    Converts `h.Primitive` instances to process-defined `ExternalModule`s
    during circuit compilation.
    """

    def __init__(self):
        super().__init__()
        # Caches of our external module calls
        self.mos_modcalls = {}
        self.res_modcalls = {}
        self.cap_modcalls = {}
        self.diode_modcalls = {}
        self.bjt_modcalls = {}

    def visit_external_module_call(self, call: h.ExternalModuleCall) -> h.Instantiable:
        """Generic logic cells (inverter, nor2, nand2) and the clock XOR become SG13G2 standard cells."""
        from flow.circuit.cells import substitute

        from . import cells

        wrapper = substitute(call, cells)  # a generic cell (flow.circuit.cells): its library cell
        if wrapper is not None:
            return wrapper
        if call.module.domain == "generic" and call.module.name in ("inverter", "nor2", "nand2"):
            from .logic import logic_cell

            return logic_cell(call.module.name, call.params)
        if call.module.domain == "generic" and call.module.name == "clock_xor":
            from .logic import clock_xor

            return clock_xor(call.params)
        return call

    def visit_primitive_call(self, call: h.PrimitiveCall) -> h.Instantiable:
        """Replace instances of `h.Primitive` with IHP `ExternalModule`s."""

        if call.prim is Mos:
            return self.mos_module_call(call.params)

        elif call.prim is PhysicalResistor or call.prim is ThreeTerminalResistor:
            return self.res_module_call(call.params)

        elif call.prim is PhysicalCapacitor or call.prim is ThreeTerminalCapacitor:
            return self.cap_module_call(call.params)

        elif call.prim is Diode:
            return self.diode_module_call(call.params)

        elif call.prim is Bipolar:
            return self.bjt_module_call(call.params)

        else:
            # Return everything else as-is
            return call

    def mos_module(self, params: MosParams) -> h.ExternalModule:
        """Retrieve or create an `ExternalModule` for MOS parameters `params`."""

        # If model name is specified directly, look it up
        if params.model is not None:
            try:
                return next(v for k, v in xtors.items() if params.model in k)
            except StopIteration:
                msg = f"No Mos module for model name {params.model}"
                raise RuntimeError(msg)

        # Otherwise, select based on MosType, MosVth, MosFamily
        mostype = h.MosType.NMOS if params.tp is None else params.tp
        mosfam = h.MosFamily.CORE if params.family is None else params.family
        if mosfam == h.MosFamily.NONE:
            mosfam = h.MosFamily.CORE

        # IHP transistor wrappers expose only `STD` Vth variants.
        # Normalize generic LOW/HIGH requests onto the available model flavor.
        mosvth = h.MosVth.STD if params.vth is None else params.vth
        if mosvth in {h.MosVth.LOW, h.MosVth.HIGH}:
            mosvth = h.MosVth.STD
        args = (mostype, mosfam, mosvth)

        # Find matching transistor
        subset = {}
        for k, v in xtors.items():
            match = True
            for a in args:
                if a not in k:
                    match = False
                    break
            if match:
                subset[k] = v

        if not subset:
            msg = f"No MOS device found for parameters: type={mostype}, family={mosfam}, vth={mosvth}"
            raise RuntimeError(msg)

        # Return the first match
        return next(iter(subset.values()))

    def mos_module_call(self, params: MosParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for MOS parameters `params`."""

        # Check cache first
        if params in CACHE.mos_modcalls:
            return CACHE.mos_modcalls[params]

        # Get the ExternalModule
        mod = self.mos_module(params)

        # Get default sizes
        w, l = self.use_defaults(params, mod.name, default_xtor_size)

        # Select appropriate parameter class based on device type
        if "hv" in mod.name:
            defaults = IhpMosHvParams.default_instance()
            modparams = IhpMosHvParams(
                w=w,
                l=l,
                ng=params.nf or defaults.ng,
                m=params.mult or defaults.m,
            )
        else:
            defaults = IhpMosParams.default_instance()
            modparams = IhpMosParams(
                w=w,
                l=l,
                ng=params.nf or defaults.ng,
                m=params.mult or defaults.m,
            )

        # Create call, cache, and return
        modcall = mod(modparams)
        CACHE.mos_modcalls[params] = modcall
        return modcall

    def res_module(self, params: PhysicalResistorParams) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for resistor parameters `params`."""

        mod = ress.get(params.model, None)
        if mod is None:
            msg = f"No Res module for model {params.model}. Available: {list(ress.keys())}"
            raise RuntimeError(msg)
        return mod

    def res_module_call(self, params: PhysicalResistorParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for resistor parameters `params`."""

        if params in CACHE.res_modcalls:
            return CACHE.res_modcalls[params]

        mod = self.res_module(params)
        w, l = self.use_defaults(params, mod.name, default_res_size)

        # PhysicalResistorParams doesn't have mult, so default to 1
        modparams = IhpResParams(w=w, l=l, m=1)

        modcall = mod(modparams)
        CACHE.res_modcalls[params] = modcall
        return modcall

    def cap_module(self, params: Any) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for capacitor parameters `params`."""

        mod = caps.get(params.model, None)
        if mod is None:
            # Check varicaps
            mod = varicaps.get(params.model, None)
        if mod is None:
            msg = f"No Cap module for model {params.model}. Available: {list(caps.keys()) + list(varicaps.keys())}"
            raise RuntimeError(msg)
        return mod

    def cap_module_call(self, params: PhysicalCapacitorParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for capacitor parameters `params`."""

        if params in CACHE.cap_modcalls:
            return CACHE.cap_modcalls[params]

        mod = self.cap_module(params)
        w, l = self.use_defaults(params, mod.name, default_cap_size)

        defaults = IhpCapParams.default_instance()
        m = int(params.mult) if params.mult is not None else defaults.m

        modparams = IhpCapParams(w=w, l=l, m=m)

        modcall = mod(modparams)
        CACHE.cap_modcalls[params] = modcall
        return modcall

    def diode_module(self, params: DiodeParams) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for diode parameters `params`."""

        # Check regular diodes first
        mod = diodes.get(params.model, None)
        if mod is None:
            # Check ESD devices
            mod = esd_devices.get(params.model, None)
        if mod is None:
            msg = (
                f"No Diode module for model {params.model}. Available: {list(diodes.keys()) + list(esd_devices.keys())}"
            )
            raise RuntimeError(msg)
        return mod

    def diode_module_call(self, params: DiodeParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for diode parameters `params`."""

        if params in CACHE.diode_modcalls:
            return CACHE.diode_modcalls[params]

        mod = self.diode_module(params)

        defaults = IhpDiodeParams.default_instance()

        if params.w is not None and params.l is not None:
            # One anode of the given width and length
            modparams = IhpDiodeParams(w=params.w, l=params.l, m=defaults.m)
        else:
            modparams = IhpDiodeParams()

        modcall = mod(modparams)
        CACHE.diode_modcalls[params] = modcall
        return modcall

    def bjt_module(self, params: BipolarParams) -> h.ExternalModule:
        """Retrieve an `ExternalModule` for bipolar parameters `params`."""

        mod = bjts.get(params.model, None)
        if mod is None:
            # Default to npn13G2 for NPN, pnpMPA for PNP
            if params.tp == h.BipolarType.PNP:
                mod = bjts.get("pnpMPA", None)
            else:
                mod = bjts.get("npn13G2", None)

        if mod is None:
            msg = f"No Bipolar module for model {params.model}. Available: {list(bjts.keys())}"
            raise RuntimeError(msg)
        return mod

    def bjt_module_call(self, params: BipolarParams) -> h.ExternalModuleCall:
        """Retrieve or create a `Call` for bipolar parameters `params`."""

        if params in CACHE.bjt_modcalls:
            return CACHE.bjt_modcalls[params]

        mod = self.bjt_module(params)

        # Determine parameter class based on device type
        if "pnp" in mod.name.lower():
            defaults = IhpPnpParams.default_instance()
            modparams = IhpPnpParams(
                a=defaults.a,
                p=defaults.p,
                m=int(params.mult) if params.mult is not None else defaults.m,
            )
        else:
            defaults = IhpHbtParams.default_instance()
            modparams = IhpHbtParams(
                Nx=defaults.Nx,
                Ny=defaults.Ny,
                m=int(params.mult) if params.mult is not None else defaults.m,
            )

        modcall = mod(modparams)
        CACHE.bjt_modcalls[params] = modcall
        return modcall

    def scale_param(self, orig: h.Scalar | None, default: h.Prefixed) -> h.Scalar:
        """
        Scale device parameter value.

        Unitless generic values are interpreted as multipliers of PDK default
        device dimensions (per-model `default_*_size` entries).
        """
        if orig is None:
            return default
        if isinstance(orig, h.Prefixed):
            if orig.prefix == h.Prefix.UNIT:
                return orig.number * default
            return orig
        if isinstance(orig, (int, float)):
            return h.Prefixed.new(orig, h.Prefix.UNIT) * default
        if isinstance(orig, h.Literal):
            return h.Literal(f"({orig.text} * {default.number}e{default.prefix.value})")
        raise TypeError(f"Param Value {orig}")

    def use_defaults(
        self,
        params: h.paramclass,
        modname: str,
        defaults: dict[str, tuple[h.Prefixed, h.Prefixed]],
    ) -> tuple[h.Scalar, h.Scalar]:
        """Get width and length, scaling unitless values by model defaults."""

        default_pair = defaults.get(modname)
        if default_pair is None:
            default_pair = next(iter(defaults.values()))
        w0, l0 = default_pair

        w = self.scale_param(getattr(params, "w", None), w0)
        l = self.scale_param(getattr(params, "l", None), l0)
        return w, l


def compile(src: h.Elaboratables) -> None:
    """
    Compile the given `src` into the IHP SG13G2 technology.

    This function uses the IhpWalker class to walk through the hierarchy of the input
    and replace instances of h.Primitive with IHP-specific ExternalModules.

    Args:
        src: The input source representing the circuit to be compiled.

    Returns:
        None
    """
    IhpWalker().walk(src)
