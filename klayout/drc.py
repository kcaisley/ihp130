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
    """The violated rules and their counts; raises when the deck is missing or writes no report
    (run_drc.py exits nonzero on violations too, so its report decides)."""

    if not (DECK / "run_drc.py").is_file():
        raise FileNotFoundError(f"no IHP DRC deck at {DECK}: set IHP_OPEN_PDK to a full IHP-Open-PDK checkout")
    run_dir.mkdir(parents=True, exist_ok=True)
    for old in run_dir.glob("*.lyrdb"):
        old.unlink()
    done = subprocess.run(
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
        text=True,
    )
    (run_dir / "run_drc.log").write_text(done.stdout + done.stderr)
    reports = list(run_dir.glob("*.lyrdb"))
    if not reports:
        raise RuntimeError(f"KLayout DRC wrote no report; see {run_dir / 'run_drc.log'}")
    counts: Counter[str] = Counter()
    for f in reports:
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
