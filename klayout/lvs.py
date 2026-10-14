"""SG13G2 LVS with the IHP open PDK's KLayout deck: CORRECT or not.

    uv run python pdk/ihp130/klayout/lvs.py GDS TOP SOURCE SOURCE_TOP RUN_DIR

The deck pairs the top cells by name: the source's top subcircuit is renamed to the layout's.

The deck: ``$IHP_OPEN_PDK`` (default ~/Documents/libs/IHP-Open-PDK)/ihp-sg13g2/libs.tech/klayout/tech/lvs.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

DECK = (
    Path(os.environ.get("IHP_OPEN_PDK", "~/Documents/libs/IHP-Open-PDK")).expanduser()
    / "ihp-sg13g2/libs.tech/klayout/tech/lvs"
)


def lvs(gds: Path, top: str, source: Path, source_top: str, run_dir: Path) -> tuple[bool, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    renamed = run_dir / "source.cdl"
    renamed.write_text(
        re.sub(rf"(?im)^(\.subckt|\.ends)(\s+){re.escape(source_top)}\b", rf"\1\2{top}", source.read_text())
    )
    source = renamed
    cmd = [
        "uv",
        "run",
        "--with",
        "docopt",
        "python",
        str(DECK / "run_lvs.py"),
        f"--layout={gds}",
        f"--netlist={source}",
        f"--topcell={top}",
        f"--run_dir={run_dir}",
        "--combine_devices",
        "--top_lvl_pins",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=False)
    (run_dir / "run_lvs.log").write_text(out.stdout + out.stderr)
    text = out.stdout + out.stderr
    ok = "Congratulations! Netlists match" in text
    return ok, run_dir / "run_lvs.log"


if __name__ == "__main__":
    ok, log = lvs(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), sys.argv[4], Path(sys.argv[5]))
    print(f"LVS {'CORRECT' if ok else 'INCORRECT'}: {log}")
