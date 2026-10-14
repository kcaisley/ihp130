"""Where the row cells find the sg13g2 standard cells and the access points derived from them.

No dependencies, so ALIGN's own Python can import it too. Each path can be overridden by the
environment variable of the same name.

- ``SG13G2_STDCELL``: the library directory of the IHP open PDK (libs.ref/sg13g2_stdcell);
  without it, this PDK's copy (``openroad/``).
- ``STEMS_ACCESS``: the cells' pin access points, written by ``stdcell_access.py`` into the
  superproject's ``build/layout/stems/``.
"""

import os
from pathlib import Path

_COPY = Path(__file__).resolve().parents[1] / "openroad"

if "SG13G2_STDCELL" in os.environ:
    _LIB = Path(os.environ["SG13G2_STDCELL"]).expanduser()
    STD_GDS = _LIB / "gds/sg13g2_stdcell.gds"
    STD_SPICE = _LIB / "cdl/sg13g2_stdcell.cdl"
    STD_LEF = _LIB / "lef/sg13g2_stdcell.lef"
else:
    STD_GDS = _COPY / "gds/sg13g2_stdcell.gds.gz"
    STD_SPICE = _COPY / "sp/sg13g2_stdcell.sp"
    STD_LEF = _COPY / "lef/sg13g2_stdcell.lef"
ACCESS_JSON = Path(
    os.environ.get("STEMS_ACCESS", Path(__file__).resolve().parents[3] / "build/layout/stems/sg13g2_access.json")
)
