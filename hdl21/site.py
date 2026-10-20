"""Site-local IHP SG13G2 installation."""

import os
from pathlib import Path

from .pdk_logic import Install

PDK_PATH = Path("/eda/kits/IHP/IHP-SG13G2")
# the IHP open PDK's ngspice models and standard-cell netlist, and its Verilog-A models compiled
# for ngspice (OpenVAF): ngspice reads these, Spectre the kit above
OPEN_PDK_PATH = Path(os.environ.get("IHP_OPEN_PDK", "/users/kcaisley/Documents/libs/IHP-Open-PDK"))
OSDI_PATH = Path(os.environ.get("IHP_OSDI", "/local/kcaisley/tools/osdi/ihp-sg13g2"))
install = Install(pdk_path=PDK_PATH, open_pdk_path=OPEN_PDK_PATH, osdi_path=OSDI_PATH)
MODEL_FILES = tuple(install.pdk_path / relative for relative in Install.LOCAL_SPICE_FILES)
