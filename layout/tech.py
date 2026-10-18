"""IHP SG13G2 values for the row cells (flow/layout/stems), all in nm.

The generic cells import this module as ``tech``, so this directory goes on the path ahead of
theirs. Rule values are SG13G2's (SG13G2_os_layout_rules.pdf, rule names in the comments); row
positions follow the sg13g2_stdcell library (3.78 um, 9 tracks of 0.42 um, 0.48 um sites, VSS
on even rail lines). Only P+ is drawn (pSD): N+ is any diffusion outside it, so NP and the VT
layers are None (not drawn).
"""

# ---- layers (GDS layer, datatype)
LAYERS = {
    "OD": (1, 0),  # Activ
    "PO": (5, 0),  # GatPoly
    "CO": (6, 0),  # Cont
    "M1": (8, 0),
    "V1": (19, 0),
    "M2": (10, 0),
    "V2": (29, 0),
    "M3": (30, 0),
    "NW": (31, 0),
    "PP": (14, 0),  # pSD
    "SALBLOCK": (28, 0),  # SalBlock: silicide block
    "POLYRES": (128, 0),  # PolyRes: poly resistor marker
    "EXTBLOCK": (111, 0),  # EXTBlock: with PolyRes, marks a poly resistor for LVS
    "NP": None,  # nSD is not drawn
    "VTN": None,
    "VTP": None,
    "BND": (189, 4),  # prBoundary.boundary, as the standard cells
    "V3": (49, 0),
    "M4": (50, 0),
    "V4": (66, 0),
    "M5": (67, 0),
    "V5": (125, 0),  # TopVia1
    "M6": (126, 0),  # TopMetal1
    "V6": (133, 0),  # TopVia2
    "M7": (134, 0),  # TopMetal2
    "TEXT": (63, 0),
    **{f"M{n}.PIN": (m, 2) for n, m in enumerate((8, 10, 30, 50, 67, 126, 134), 1)},  # Metal<n>.pin
}
LAYER_NAMES = {f"M{n}": f"Metal{n}" for n in range(1, 6)}  # the layer map's names (the hosted laygo server's)
PIN_TEXT = {"M1": (8, 25), "M2": (10, 25), "M3": (30, 25)}  # Metal<n>.text: pin labels
MODELS = {"n": "sg13_lv_nmos", "p": "sg13_lv_pmos"}  # LVS device names of the row transistors
STD_LIB = "sg13g2_stdcell"  # the standard-cell library
MFG_GRID = 5  # manufacturing grid
DBU = 0.001  # um per database unit (1 nm)

# ---- metal and via rules, the whole stack (generators beyond the rows: the caparray), from the
# tech LEF (openroad/): metal width, space, pitch, area (nm2); via cut (square) and space between
# cuts. Rules the LEF holds only in tables (enclosures, conditional spacing) are left out.
RULES = {
    "M1": {"width": 160, "space": 180, "pitch": 420, "area": 90_000},
    # enclosure: (on two opposite sides, on the other two, on all four), the PDK's via rules (an end
    # cap of 50 nm, 10 nm elsewhere); enclosed_area: the LEF gives none, a conservative 1 um2
    **{f"V{n}": {"cut": 190, "space": 220, "enclosure": (50, 10, 10)} for n in range(1, 5)},
    **{
        f"M{n}": {"width": 200, "space": 210, "pitch": 480, "area": 144_000, "enclosed_area": 1_000_000} for n in (2, 4)
    },
    **{
        f"M{n}": {"width": 200, "space": 210, "pitch": 420, "area": 144_000, "enclosed_area": 1_000_000} for n in (3, 5)
    },
    "V5": {"cut": 420, "space": 420},
    "M6": {"width": 1640, "space": 1640, "pitch": 2280},
    "V6": {"cut": 900, "space": 1060},
    "M7": {"width": 2000, "space": 2000, "pitch": 4000},
}
NW_SPACE = 620  # NW.b: N-well space, narrower gaps are closed

# ---- the standard-cell row
H = 3780  # row height; rails at 0 (VSS) and H (VDD)
PITCH = 420  # M2 track pitch (y), tracks on multiples of it
XPITCH = 480  # M3 track pitch and cell width grid (x): the library's site width
RAIL = 220  # M1 rail half width (440 nm, as the std cells)
TAP_OD = 150  # tap diffusion half height under the rails
TAP_PITCH = 480  # tap contacts at x = TAP_PITCH / 2 + k * TAP_PITCH
PP_TAP = 180  # P tap pSD band top (bottom -PP_TAP), as the library
NP_TAP = 3600  # top of a PMOS cell's pSD: 30 nm from the N tap diffusion (pSD.d1)
NW_N, NW_P, NW_TOP = (
    3320,
    390,
    4170,
)  # well: N-tap band bottom (NW.d 310 from the tap where a PMOS well steps down), PMOS body bottom (NW.f 240), top
VT_BAND = (180, 3600)  # no VT layer drawn
STD_NW = 1750  # library cells: well from here (their pSD from 1760)
IMP_OH, NW_OH = 70, 240  # overhang of the tap pSD band and the N-tap well band past a cell

# ---- the standard cells next to the rows (stdcell_access.py, netcells.py)
STD_CELLS = ("sg13g2_inv_1", "sg13g2_inv_4", "sg13g2_inv_8", "sg13g2_nor2_2", "sg13g2_nand2_2", "sg13g2_fill_1")
STD_SUPPLY = ("VDD", "VSS")  # supply pin names, VDD rail on top
STD_FILL, STD_FILL_W = "sg13g2_fill_1", 480  # one-site filler
STD_TEXT_LAYERS: set[int] = set()  # labels sit on the metal layers' text datatype: netcells drops all text
STD_TRACKS = (1680, 2100, 1260, 2520, 840, 2940)  # pin access tracks, preferred first (middle of the cell)
STD_WIDE = None  # one VIA1 on any plate (two only above 1.4 um, MINIMUMCUT)
ISO_PAD = 240  # isolated std cells: pad on both sides, the library cell's well overhang
EDGE_CUTS, EDGE_PAD = 1, (360, 100)  # row-end supply stack: one VIA1 per rail, M2 pad 720 x 200 (Mn.d)

# ---- device placement in the row
GATE_TRACK = {"n": 2940, "p": 840}  # gate bar and its M2 track
SD_TRACKS = {"n": (840, 1260, 1680, 2100), "p": (2940, 2520, 2100, 1680)}  # S/D M2 tracks
# NMOS: 300 nm from the tap pSD (pSD.j), gate contact 140 nm from the diffusion (Cnt.e);
# PMOS: gate 300 nm inside pSD (pSD.i), 670 nm inside the well (NW.c 310)
OD_LIMIT = {"n": (480, 2720), "p": (1060, 3300)}  # (OD start at the rail side, furthest OD edge)
W_MAX = 2240  # widest finger
EDGE = 310  # OD to the cell edge: NW.c / NW.d against any neighbour's well, pSD.j against its pSD
OD_GAP = 210  # diffusion break between a pair's devices that share no strip (Act.b)
GATE_GAP = 520  # gate to gate across a shared strip when the gates differ (their M2 bars, Mn.b)

# ---- rule-derived dimensions
CO = 160  # Cnt.a (exact size)
CO_PITCH = 340  # contacts along a strip (Cnt.b 180)
CO_GATE = 110  # contact to gate (Cnt.f): the contacted pitch is L + CO + 2 CO_GATE
CO_OD_END, CO_OD_SIDE = 70, 70  # Activ enclosure of the contacts (Cnt.c)
OD_EXT = 150  # OD past the outermost strip centre (CO / 2 + Cnt.c)
V1, V2 = RULES["V1"]["cut"], RULES["V2"]["cut"]  # Via1 / Via2 (V1.a, Vn.a)
M1W, M2W, M3W = 210, 200, 200  # M1 strips and pads (Via1 + 2 x V1.c), M2 / M3 bars (Via + 2 x Vn.c)
M1_CO_END = 50  # M1 past a contact along a strip (M1.c1)
M1_SPACE = RULES["M1"]["space"]  # M1.b
M1_MIN_W = 160  # M1.a: narrowest M1 a pin access may use
V1_PAIR = 410  # two Via1 side by side, centre to centre (V1.b 220)
M1_MIN_LEN = 430  # an M1W-wide M1 piece meets M1.d (0.09 um2)
M1_BAR_MIN = 320  # shortest gate M1 bar, and the area that forces it
M1_AREA = RULES["M1"]["area"]
M2_SPACE = RULES["M2"]["space"]  # Mn.b
M2_MIN_LEN = 780  # an M2W-wide M2 / M3 piece meets Mn.d (720 nm), and spans an M3 track: XPITCH + 2 BAR_END
BAR_END = 145  # a bar past its outermost via centre (V / 2 + Vn.c1 / V1.c1 50)
GATE_PAD = 145  # M1 pad half height around a gate contact
PO_ENDCAP = 180  # poly past OD (Gat.c)
PO_HEAD = 150  # poly head half height around a gate contact (CO / 2 + Cnt.d 70)
PO_BAR_END = 150  # poly bar past its outer gates (CO / 2 + Cnt.d)
SHORT_L = 400  # shorter gates leave room for the gate pads beside the S/D contacts (M1.b)
M1_EDGE, M2_EDGE, M3_EDGE = 90, 105, 240  # bars kept from the cell edge
ALIGN_ROUTER = "hanan"  # ALIGN's router: its default (astar) leaves long nets across these rows open
LAYGO_CLEAR = 210  # laygo: a bar's end to a pin bar booked END wider (Mn.b)
LAYGO_LINE_END = False  # no dense line-end rule
LAYGO_GAP3 = 500  # laygo: M3 segments booked by their via centres, drawn BAR_END further: 2 BAR_END + Mn.b

# the metals a fringe MOM capacitor stacks (flow/momcap), from the top: the upper uniform thin
# metals at their minimum width and space; an N-layer unit uses the top N, its shield the metal
# below them
MOM_LAYERS = (3, 4, 5)

# the unsilicided P+ poly resistor rppd (flow/layout/stems/rescell.py): its LVS device (PolyRes,
# pSD and SalBlock over GatPoly) and model (rsh 260, weff = w + 6 nm, rz 35 ohm um per head); Rppd.a
# (width); PolyRes marks the body, SalBlock the body and 0.2 past the poly across it (Sal.c), the
# contacts 0.2 from it (Sal.d), EXTBlock over the whole resistor as its pSD (PolyRes and EXTBlock
# mark the device), as the kit's own LVS test layouts; pSD past the resistor (pSD.n, Rppd.b); Cnt.d
RES = {
    "model": "rppd",
    "sheet": 260.0,
    "dw": -6,
    "end": 70.0,
    "width": 500,
    "markers": {"SALBLOCK": (0, 200), "POLYRES": (0, 0), "EXTBLOCK": (630, 200)},
    "implant": ("PP", 200),
    "co_space": 200,
    "co_enc": 70,
    "cdl": "R{name} {plus} {minus} rppd m=1 l={l}u w={w}u",
    "bulk": True,  # the model's third terminal, the substrate
    "sim_model": "res_rppd",  # the simulation library's name for it  # as the deck's own test netlists
}

# FMOM capacitance per (style, stacked metals): rows (plate spacing nm, slope fF/um, intercept
# fF), C = slope * L + intercept, at 1, 1.5, 2 and 3 times the metals' minimum spacing. Estimated,
# not extracted (no 3D extraction deck for this kit): the alpha / s + beta fits of the 65 and 180 nm extractions, geometric in log(node)
# (flow/momcap readme); generators interpolate in 1 / spacing at the spacing they draw
MOM_MODEL = {
    ("difference", 1): ((210, 0.1929, 0.0572), (315, 0.1379, 0.0572), (420, 0.11, 0.0572), (630, 0.0815, 0.0572)),
    ("difference", 2): ((210, 0.3946, 0.1411), (315, 0.2847, 0.1411), (420, 0.2291, 0.1411), (630, 0.1726, 0.1411)),
    ("difference", 3): ((210, 0.5946, 0.227), (315, 0.4297, 0.227), (420, 0.3463, 0.227), (630, 0.2617, 0.227)),
    ("ring", 1): ((210, 0.1905, 0.0879), (315, 0.1371, 0.0879), (420, 0.1101, 0.0879), (630, 0.0825, 0.0879)),
    ("ring", 2): ((210, 0.3908, 0.2155), (315, 0.2839, 0.2155), (420, 0.2299, 0.2155), (630, 0.1749, 0.2155)),
    ("ring", 3): ((210, 0.5895, 0.3422), (315, 0.4288, 0.3422), (420, 0.3475, 0.3422), (630, 0.265, 0.3422)),
    ("strip", 1): ((210, 0.105, 0.0055), (315, 0.0741, 0.0055), (420, 0.0585, 0.0055), (630, 0.0425, 0.0055)),
    ("strip", 2): ((210, 0.2139, 0.0366), (315, 0.1526, 0.0366), (420, 0.1215, 0.0366), (630, 0.09, 0.0366)),
    ("strip", 3): ((210, 0.3212, 0.0709), (315, 0.2297, 0.0709), (420, 0.1834, 0.0709), (630, 0.1364, 0.0709)),
}
