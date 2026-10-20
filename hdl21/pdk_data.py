# Std-Lib Imports
from copy import deepcopy

# Hdl21 Imports
import hdl21 as h
from hdl21.prefix import µ
from hdl21.primitives import (
    Bipolar,
    Diode,
    PhysicalCapacitor,
    PhysicalResistor,
    ThreeTerminalCapacitor,
    ThreeTerminalResistor,
)

# Vlsirtool Types to ease downstream parsing
from vlsirtools import SpiceType

PDK_NAME = "ihp"

"""
Parameter classes for IHP SG13G2 130nm BiCMOS PDK devices.

This PDK features:
- Low-voltage (1.2V) and High-voltage (3.3V) CMOS transistors
- High-performance SiGe HBTs with fT up to 350 GHz
- Various resistor types (rsil, rhigh, rppd)
- MIM capacitors and varactors
- ESD protection diodes and Schottky diodes
"""


@h.paramclass
class IhpMosParams:
    """
    IHP SG13G2 Low-Voltage MOS Parameters.

    These parameters match the sg13_lv_nmos/pmos subcircuit interface. Sizes are in
    meters, as the models take them.

    Attributes:
        w: Width. Default is 0.35µm (minimum).
        l: Length. Default is 0.13µm (minimum for LV).
        ng: Number of gate fingers. Default is 1.
        m: Multiplier. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width", default=0.35 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length", default=0.13 * µ)
    ng = h.Param(dtype=h.Scalar, desc="Number of gate fingers", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpMosHvParams:
    """
    IHP SG13G2 High-Voltage MOS Parameters.

    For sg13_hv_nmos/pmos subcircuits (3.3V devices).
    Minimum length is 0.45µm for HV devices.

    Attributes:
        w: Width. Default is 0.35µm.
        l: Length. Default is 0.45µm (minimum for HV).
        ng: Number of gate fingers. Default is 1.
        m: Multiplier. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width", default=0.35 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length", default=0.45 * µ)
    ng = h.Param(dtype=h.Scalar, desc="Number of gate fingers", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpHbtParams:
    """
    IHP SG13G2 HBT (npn13G2) Parameters.

    High-performance SiGe:C npn-HBT with fT up to 350 GHz.
    The emitter geometry is defined by Nx and Ny (emitter array).

    Attributes:
        Nx: Number of emitters in X direction. Default is 1.
        Ny: Number of emitters in Y direction. Default is 1.
        m: Multiplier. Default is 1.
    """

    Nx = h.Param(dtype=h.Scalar, desc="Number of emitters in X", default=1)
    Ny = h.Param(dtype=h.Scalar, desc="Number of emitters in Y", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpPnpParams:
    """
    IHP SG13G2 Lateral PNP (pnpMPA) Parameters.

    The model's own (the kit's and the open PDK's): the emitter's area and perimeter, which a
    drawn emitter of width w and length l gives as w * l and 2 * (w + l).

    Attributes:
        a: Emitter area in m². Default is 2µm² (1µm by 2µm).
        p: Emitter perimeter in m. Default is 6µm.
        m: Multiplier. Default is 1.
    """

    a = h.Param(dtype=h.Scalar, desc="Emitter area in m²", default=2e-12)
    p = h.Param(dtype=h.Scalar, desc="Emitter perimeter", default=6 * µ)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpResParams:
    """
    IHP SG13G2 Resistor Parameters.

    For rsil, rhigh, and rppd resistors (3-terminal with bulk).

    Attributes:
        w: Width. Default is 0.5µm.
        l: Length. Default is 2.0µm.
        m: Multiplier. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width", default=0.5 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length", default=2.0 * µ)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpCapParams:
    """
    IHP SG13G2 MIM Capacitor Parameters.

    For cap_cmim and cap_rfcmim capacitors.

    Attributes:
        w: Width. Default is 6.0µm (minimum).
        l: Length. Default is 6.0µm (minimum).
        m: Multiplier. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width", default=6.0 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length", default=6.0 * µ)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpVaricapParams:
    """
    IHP SG13G2 Varactor (sg13_hv_svaricap) Parameters.

    4-terminal varactor device (G1, W, G2, bn).

    Attributes:
        w: Width. Default is 1.0µm.
        l: Length. Default is 1.0µm.
        m: Multiplier. Default is 1.
    """

    w = h.Param(dtype=h.Scalar, desc="Width", default=1.0 * µ)
    l = h.Param(dtype=h.Scalar, desc="Length", default=1.0 * µ)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpDiodeParams:
    """
    IHP SG13G2 Schottky Diode (schottky_nbl1) Parameters.

    The model's own (the kit's and the open PDK's): an array of Nx by Ny anodes of length l and
    width w.

    Attributes:
        l: Anode length. Default is 1µm.
        w: Anode width. Default is 0.3µm.
        Nx: Number of anodes in X. Default is 1.
        Ny: Number of anodes in Y. Default is 1.
        m: Multiplier. Default is 1.
    """

    l = h.Param(dtype=h.Scalar, desc="Anode length", default=1 * µ)
    w = h.Param(dtype=h.Scalar, desc="Anode width", default=0.3 * µ)
    Nx = h.Param(dtype=h.Scalar, desc="Number of anodes in X", default=1)
    Ny = h.Param(dtype=h.Scalar, desc="Number of anodes in Y", default=1)
    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpEsdParams:
    """
    IHP SG13G2 ESD Device Parameters.

    For diodevdd_2kv, diodevdd_4kv, diodevss_2kv, diodevss_4kv.
    These are 3-terminal ESD devices (VDD, PAD, VSS).

    Attributes:
        m: Multiplier. Default is 1.
    """

    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


@h.paramclass
class IhpLogicParams:
    """
    IHP SG13G2 Logic Cell Parameters.

    Parameters for digital standard cells.

    Attributes:
        m: Multiplier. Default is 1.
    """

    m = h.Param(dtype=h.Scalar, desc="Multiplier", default=1)


"""
Module creator functions for IHP SG13G2 devices.
These create ExternalModule instances representing PDK subcircuits.
"""


def xtor_module(
    modname: str,
    params: h.Param = IhpMosParams,
    num_terminals: int = 4,
) -> h.ExternalModule:
    """Create IHP MOS transistor ExternalModule.

    Args:
        modname: SPICE subcircuit name (e.g., 'sg13_lv_nmos')
        params: Parameter class for this device
        num_terminals: Number of terminals (4 for standard MOS)

    Returns:
        ExternalModule representing the MOS device
    """
    # Standard 4-terminal MOS port list: d, g, s, b
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK MOS {modname}",
        port_list=deepcopy(h.Mos.port_list),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


# 4-terminal HBT port list: c, b, e, bn (base node/substrate)
HBT4TPortList = [
    h.Port(name="c", desc="Collector"),
    h.Port(name="b", desc="Base"),
    h.Port(name="e", desc="Emitter"),
    h.Port(name="bn", desc="Base Node (Substrate)"),
]

# 5-terminal HBT port list: c, b, e, bn, t
HBT5TPortList = [
    h.Port(name="c", desc="Collector"),
    h.Port(name="b", desc="Base"),
    h.Port(name="e", desc="Emitter"),
    h.Port(name="bn", desc="Base Node (Substrate)"),
    h.Port(name="t", desc="Temperature"),
]


def hbt_module(
    modname: str,
    params: h.Param = IhpHbtParams,
    num_terminals: int = 4,
) -> h.ExternalModule:
    """Create IHP HBT (npn13G2) ExternalModule.

    IHP HBTs have 4 terminals (c, b, e, bn) or 5 terminals (c, b, e, bn, t).
    The 'bn' terminal is the base node/substrate connection.

    Args:
        modname: SPICE subcircuit name (e.g., 'npn13G2')
        params: Parameter class for this device
        num_terminals: 4 for standard HBT, 5 for 5-terminal variants

    Returns:
        ExternalModule representing the HBT device
    """
    num2ports = {4: HBT4TPortList, 5: HBT5TPortList}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK HBT {modname}",
        port_list=deepcopy(num2ports[num_terminals]),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


def pnp_module(
    modname: str,
    params: h.Param = IhpPnpParams,
) -> h.ExternalModule:
    """Create IHP PNP (pnpMPA) ExternalModule.

    Lateral PNP transistor with 3 terminals (c, b, e).

    Args:
        modname: SPICE subcircuit name (e.g., 'pnpMPA')
        params: Parameter class for this device

    Returns:
        ExternalModule representing the PNP device
    """
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK PNP {modname}",
        port_list=deepcopy(Bipolar.port_list),  # c, b, e
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


# 3-terminal resistor port list: p, n, b (bulk)
Res3TPortList = [
    h.Port(name="p", desc="Positive"),
    h.Port(name="n", desc="Negative"),
    h.Port(name="b", desc="Bulk"),
]


def res_module(
    modname: str,
    numterminals: int = 3,
    params: h.Param = IhpResParams,
) -> h.ExternalModule:
    """Create IHP resistor ExternalModule.

    IHP resistors (rsil, rhigh, rppd) are 3-terminal devices with bulk connection.

    Args:
        modname: SPICE subcircuit name (e.g., 'rsil')
        numterminals: Number of terminals (3 for IHP resistors)
        params: Parameter class for this device

    Returns:
        ExternalModule representing the resistor device
    """
    num2device = {2: PhysicalResistor, 3: ThreeTerminalResistor}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Res {modname}",
        port_list=deepcopy(num2device[numterminals].port_list),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


def cap_module(
    modname: str,
    numterminals: int = 2,
    params: h.Param = IhpCapParams,
) -> h.ExternalModule:
    """Create IHP capacitor ExternalModule.

    cap_cmim is 2-terminal (PLUS, MINUS).
    cap_rfcmim is 3-terminal (PLUS, MINUS, bn).

    Args:
        modname: SPICE subcircuit name (e.g., 'cap_cmim')
        numterminals: 2 or 3
        params: Parameter class for this device

    Returns:
        ExternalModule representing the capacitor device
    """
    num2device = {2: PhysicalCapacitor, 3: ThreeTerminalCapacitor}

    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Cap {modname}",
        port_list=deepcopy(num2device[numterminals].port_list),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


# 4-terminal varicap port list: G1, W, G2, bn
Varicap4TPortList = [
    h.Port(name="g1", desc="Gate 1"),
    h.Port(name="w", desc="Well"),
    h.Port(name="g2", desc="Gate 2"),
    h.Port(name="bn", desc="Bulk Node"),
]


def varicap_module(
    modname: str,
    params: h.Param = IhpVaricapParams,
) -> h.ExternalModule:
    """Create IHP varactor (sg13_hv_svaricap) ExternalModule.

    4-terminal varactor device for VCO and tuning applications.

    Args:
        modname: SPICE subcircuit name (e.g., 'sg13_hv_svaricap')
        params: Parameter class for this device

    Returns:
        ExternalModule representing the varicap device
    """
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Varicap {modname}",
        port_list=deepcopy(Varicap4TPortList),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


# Schottky diode port list: A, C, S (Anode, Cathode, Substrate)
Schottky3TPortList = [
    h.Port(name="a", desc="Anode"),
    h.Port(name="c", desc="Cathode"),
    h.Port(name="s", desc="Substrate"),
]

# ESD device port list: VDD, PAD, VSS
Esd3TPortList = [
    h.Port(name="vdd", desc="VDD"),
    h.Port(name="pad", desc="PAD"),
    h.Port(name="vss", desc="VSS"),
]


def diode_module(
    modname: str,
    params: h.Param = IhpDiodeParams,
) -> h.ExternalModule:
    """Create IHP diode ExternalModule.

    For standard 2-terminal diode behavior.

    Args:
        modname: SPICE subcircuit name
        params: Parameter class for this device

    Returns:
        ExternalModule representing the diode device
    """
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Diode {modname}",
        port_list=deepcopy(Diode.port_list),
        paramtype=params,
        spicetype=SpiceType.DIODE,
    )
    return mod


def schottky_module(
    modname: str,
    params: h.Param = IhpDiodeParams,
) -> h.ExternalModule:
    """Create IHP Schottky diode (schottky_nbl1) ExternalModule.

    3-terminal Schottky diode (A, C, S).

    Args:
        modname: SPICE subcircuit name (e.g., 'schottky_nbl1')
        params: Parameter class for this device

    Returns:
        ExternalModule representing the Schottky diode device
    """
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK Schottky {modname}",
        port_list=deepcopy(Schottky3TPortList),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


def esd_module(
    modname: str,
    params: h.Param = IhpEsdParams,
) -> h.ExternalModule:
    """Create IHP ESD protection device ExternalModule.

    3-terminal ESD devices (VDD, PAD, VSS).

    Args:
        modname: SPICE subcircuit name (e.g., 'diodevdd_2kv')
        params: Parameter class for this device

    Returns:
        ExternalModule representing the ESD device
    """
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{PDK_NAME} PDK ESD {modname}",
        port_list=deepcopy(Esd3TPortList),
        paramtype=params,
        spicetype=SpiceType.SUBCKT,
    )
    return mod


def logic_module(
    modname: str,
    family: str,
    terminals: list[str],
) -> h.ExternalModule:
    """Create IHP digital logic cell ExternalModule.

    Args:
        modname: Cell name
        family: Logic family name
        terminals: List of terminal names

    Returns:
        ExternalModule representing the logic cell
    """
    mod = h.ExternalModule(
        domain=PDK_NAME,
        name=modname,
        desc=f"{family} {modname} Logic Circuit",
        port_list=[h.Port(name=i) for i in terminals],
        paramtype=IhpLogicParams,
    )
    return mod
