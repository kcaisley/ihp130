"""SG13G2 DRC with the IHP open PDK's KLayout deck (no density): the violated rules and counts.

    uv run python pdk/ihp130/klayout/drc.py GDS TOP RUN_DIR

The deck: ``$IHP_OPEN_PDK`` (default ~/Documents/libs/IHP-Open-PDK)/ihp-sg13g2/libs.tech/klayout/tech/drc.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

from klayout import rdb

DECK = (
    Path(os.environ.get("IHP_OPEN_PDK", "~/Documents/libs/IHP-Open-PDK")).expanduser()
    / "ihp-sg13g2/libs.tech/klayout/tech/drc"
)


def drc(gds: Path, top: str, run_dir: Path) -> dict[str, int]:
    run_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(DECK / "run_drc.py"),
            f"--path={gds}",
            f"--topcell={top}",
            f"--run_dir={run_dir}",
            "--no_density",
            "--mp=8",
        ],
        check=False,
        capture_output=True,
    )
    counts: Counter[str] = Counter()
    for f in run_dir.glob("*.lyrdb"):
        db = rdb.ReportDatabase("")
        db.load(str(f))
        for item in db.each_item():
            counts[db.category_by_id(item.category_id()).name()] += 1
    return dict(counts)


if __name__ == "__main__":
    violations = drc(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]))
    for rule, n in sorted(violations.items()):
        print(f"{rule:24s} {n}")
    print("DRC clean" if not violations else f"DRC: {len(violations)} rules violated")
