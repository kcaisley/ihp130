"""IHP SG13G2 layout data shared by the layout tools: the layers, metal and via rules and row-cell values
(tech.py), and the standard-cell locations (paths.py)."""

# ALIGN's PDK package as well: this directory, with the files flow/layout/make_pdk.py writes,
# hands ALIGN frida's generators by name (flow/layout/package.py), loaded only when asked for
import importlib.util as _util
from pathlib import Path as _Path

_spec = _util.spec_from_file_location(
    "frida_align_package", _Path(__file__).resolve().parents[3] / "flow/layout/package.py"
)
_package = _util.module_from_spec(_spec)
_spec.loader.exec_module(_package)
__getattr__ = _package.exports(_Path(__file__).resolve().parent)
