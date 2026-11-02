"""ALIGN's ``gen_param`` for this PDK (ALIGN loads it from the PDK directory by file name): frida's,
flow/layout/align/pdk/gen_param.py, through flow/layout/align/package.py."""

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("frida_align_package", _HERE.parents[2] / "flow/layout/align/package.py")
_package = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_package)
gen_param = _package.gen_param(_HERE)
