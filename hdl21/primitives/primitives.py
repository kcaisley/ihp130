"""IHP SG13G2's devices for direct instantiation: the device dictionaries, and each device by name.

Example:
    from pdk.ihp130.hdl21.primitives.primitives import LV_NMOS

    @h.module
    class MyCircuit:
        vdd, vss, inp, out = h.Ports(4)
        n = LV_NMOS(IhpMosParams(w=1 * µ, l=0.13 * µ))(d=out, g=inp, s=vss, b=vss)
"""

from hdl21.primitives import MosFamily, MosType, MosVth

from .prim_dicts import bjts, caps, diodes, esd_devices, ress, stdcells, varicaps, xtors

__all__ = ["bjts", "caps", "diodes", "ress", "stdcells", "xtors"]

# ==== MOS Transistors ====

# Low-voltage (1.2V core) transistors - min L = 0.13µm
LV_NMOS = xtors["LV_NMOS", MosType.NMOS, MosVth.STD, MosFamily.CORE]
LV_PMOS = xtors["LV_PMOS", MosType.PMOS, MosVth.STD, MosFamily.CORE]

# High-voltage (3.3V I/O) transistors - min L = 0.45µm
HV_NMOS = xtors["HV_NMOS", MosType.NMOS, MosVth.STD, MosFamily.IO]
HV_PMOS = xtors["HV_PMOS", MosType.PMOS, MosVth.STD, MosFamily.IO]

# ==== Bipolar Transistors - HBT ====
# High-performance HBTs with fT up to 350 GHz, fmax up to 450 GHz

# Standard 4-terminal HBTs (c, b, e, bn)
NPN13G2 = bjts["npn13G2"]
NPN13G2L = bjts["npn13G2l"]
NPN13G2V = bjts["npn13G2v"]

# 5-terminal HBT variants (c, b, e, bn, t)
NPN13G2_5T = bjts["npn13G2_5t"]
NPN13G2L_5T = bjts["npn13G2l_5t"]
NPN13G2V_5T = bjts["npn13G2v_5t"]

# ==== Bipolar Transistors - Lateral PNP ====

# Lateral PNP transistor (3-terminal: c, b, e)
PNPMPA = bjts["pnpMPA"]

# ==== Resistors (3-Terminal with Bulk Connection) ====

# Silicided polysilicon resistor (~7 ohm/sq)
RSIL = ress["rsil"]

# High-resistivity polysilicon resistor (~1k ohm/sq)
RHIGH = ress["rhigh"]

# P-doped polysilicon resistor (~300 ohm/sq)
RPPD = ress["rppd"]

# ==== Capacitors ====

# MIM capacitor (2-terminal: PLUS, MINUS)
CAP_CMIM = caps["cap_cmim"]

# RF MIM capacitor (3-terminal: PLUS, MINUS, bn)
CAP_RFCMIM = caps["cap_rfcmim"]

# Varactor (4-terminal: G1, W, G2, bn)
SVARICAP = varicaps["sg13_hv_svaricap"]

# ==== Diodes ====

# Schottky diode (3-terminal: A, C, S)
SCHOTTKY_NBL1 = diodes["schottky_nbl1"]

# ==== ESD Protection Devices (3-Terminal: VDD, PAD, VSS) ====

DIODEVDD_2KV = esd_devices["diodevdd_2kv"]
DIODEVDD_4KV = esd_devices["diodevdd_4kv"]
DIODEVSS_2KV = esd_devices["diodevss_2kv"]
DIODEVSS_4KV = esd_devices["diodevss_4kv"]
