"""Site-local IHP SG13G2 installation."""

from pathlib import Path

from .pdk_logic import Install

PDK_PATH = Path("/eda/kits/IHP/IHP-SG13G2")
install = Install(pdk_path=PDK_PATH)
MODEL_FILES = tuple(install.pdk_path / relative for relative in Install.LOCAL_SPICE_FILES)
