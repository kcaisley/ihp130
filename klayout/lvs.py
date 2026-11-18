"""SG13G2 LVS with the IHP open PDK's KLayout deck: CORRECT or not.

    uv run python pdk/ihp130/klayout/lvs.py GDS TOP SOURCE SOURCE_TOP RUN_DIR

The deck pairs the top cells by name: the source's top subcircuit is renamed to the layout's. It
runs as the deck's own ``run_lvs.py --combine_devices --top_lvl_pins`` does (its switches given to
KLayout here), from a copy that joins each supply's labelled pieces by name (frida's
``flow.layout.klayout_lvs.joined_deck``): a block's rail lines are pins of their own, which the
converter's power grid joins.

The deck: ``$IHP_OPEN_PDK`` (default ~/Documents/libs/IHP-Open-PDK)/ihp-sg13g2/libs.tech/klayout/tech/lvs.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

DECK = (
    Path(os.environ.get("IHP_OPEN_PDK", "~/Documents/libs/IHP-Open-PDK")).expanduser()
    / "ihp-sg13g2/libs.tech/klayout/tech/lvs"
)


def lvs(gds: Path, top: str, source: Path, source_top: str, run_dir: Path) -> tuple[bool, Path]:
    if not (DECK / "sg13g2.lvs").is_file():
        raise FileNotFoundError(f"no IHP LVS deck at {DECK}: set IHP_OPEN_PDK to a full IHP-Open-PDK checkout")
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    renamed = run_dir / "source.cdl"
    renamed.write_text(
        re.sub(rf"(?im)^(\.subckt|\.ends)(\s+){re.escape(source_top)}\b", rf"\1\2{top}", source.read_text())
    )
    source = renamed
    from flow.layout.klayout_lvs import joined_deck

    deck = joined_deck(DECK / "sg13g2.lvs", run_dir / "sg13g2.lvs")
    stem = Path(gds).name.split(".")[0]
    switches = {
        "run_mode": "deep",
        "no_net_names": "false",
        "spice_comments": "false",
        "net_only": "false",
        "top_lvl_pins": "true",
        "no_simplify": "false",
        "no_series_res": "false",
        "no_parallel_res": "false",
        "combine_devices": "true",
        "purge": "false",
        "purge_nets": "false",
        "verbose": "false",
        "topcell": top,
        "input": str(Path(gds).resolve()),
        "schematic": str(source.resolve()),
        "allow_unmatched_ports": "false",
        "report": str(run_dir / f"{stem}.lvsdb"),
        "log": str(run_dir / f"{stem}.log"),
        "target_netlist": str(run_dir / f"{stem}_extracted.cir"),
    }
    cmd = ["klayout", "-b", "-r", str(deck)]
    for key, value in switches.items():
        cmd += ["-rd", f"{key}={value}"]
    from flow.logs import run_logged

    # its whole output in run_lvs.log and the flow's log (klayout.lvs), a mismatch not a failure
    text = run_logged(cmd, cwd=run_dir, log=run_dir / "run_lvs.log", name="klayout.lvs", allowed=tuple(range(256)))
    ok = "Congratulations! Netlists match" in text
    return ok, run_dir / "run_lvs.log"


if __name__ == "__main__":
    ok, log = lvs(Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), sys.argv[4], Path(sys.argv[5]))
    print(f"LVS {'CORRECT' if ok else 'INCORRECT'}: {log}")
