"""Signoff provider for frida's ``flow/layout/signoff.py``: DRC and LVS of a block in IHP SG13G2.

DRC: the gdscheck precheck (``gdscheck/pdk.yml``) where gdscheck is installed, then the IHP open
PDK's KLayout deck without density (``klayout/drc.py``). LVS: its KLayout deck (``klayout/lvs.py``).
Both need a full IHP-Open-PDK checkout (``IHP_OPEN_PDK``). The checkers run in ``drc/`` and ``lvs/``
under the run directory. No PEX here.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from klayout import rdb

from pdk.ihp130.klayout.drc import drc
from pdk.ihp130.klayout.lvs import lvs

PRECHECK = Path(__file__).resolve().parent / "gdscheck" / "pdk.yml"


def _gdscheck(gds_path: Path, layout_top: str, run_dir: Path) -> dict[str, int]:
    """The precheck's violations per rule (``gdscheck:<rule>``); none where gdscheck is not installed."""

    executable = shutil.which("gdscheck")
    if executable is None:
        return {}
    report = run_dir / "gdscheck.lyrdb"
    report.unlink(missing_ok=True)
    command = [executable, "run", "-i", str(gds_path), "-p", str(PRECHECK), "-t", layout_top, "-s", "precheck"]
    done = subprocess.run([*command, "-r", str(report)], capture_output=True, text=True, check=False)
    (run_dir / "gdscheck.log").write_text(done.stdout + done.stderr)
    if not report.exists():
        raise RuntimeError(f"gdscheck wrote no report; see {run_dir / 'gdscheck.log'}")
    db = rdb.ReportDatabase("")
    db.load(str(report))
    counts: dict[str, int] = {}
    for item in db.each_item():
        rule = f"gdscheck:{db.category_by_id(item.category_id()).name()}"
        counts[rule] = counts.get(rule, 0) + 1
    return counts


def _report(run_dir: Path, checker: str, found: dict[str, int], waived: re.Pattern[str] | None) -> Path:
    """``drc_violations.json``: the violated rules and the waived ones, with counts; raises when a
    rule outside the waivers is violated."""

    skip = {rule: n for rule, n in found.items() if waived is not None and waived.match(rule)}
    violations = {rule: n for rule, n in found.items() if rule not in skip}
    report = run_dir / "drc_violations.json"
    report.write_text(json.dumps({"checker": checker, "violations": violations, "waived": skip}, indent=1) + "\n")
    if violations:
        raise RuntimeError(f"DRC: {len(violations)} rules violated; see {report}")
    return report


def run_drc(*, run_dir: Path, gds_path: Path, layout_top: str, options: object = None) -> Path:
    """gdscheck, then KLayout DRC; returns ``drc_violations.json`` and raises unless clean."""

    work = run_dir / "drc"
    work.mkdir(parents=True, exist_ok=True)
    found = _gdscheck(gds_path, layout_top, work) | drc(gds_path, layout_top, work)
    return _report(run_dir, "klayout", found, None)


def run_lvs(
    *, run_dir: Path, gds_path: Path, source_path: Path, layout_top: str, source_top: str, options: object = None
) -> tuple[bool, Path]:
    """KLayout LVS in ``lvs/``: whether the netlists match, and its log."""

    return lvs(gds_path, layout_top, source_path, source_top, run_dir / "lvs")


KIT = Path("/eda/kits/IHP/IHP-SG13G2/SG13G2_618_rev1.2.10")


def run_layout_pex(*, run_dir: Path, gds_path: Path, layout_top: str, output_stem: str) -> Path:
    """3D xACT of a layout by its own net names (``flow.layout.calibre_pex``), in ``pex/``: the kit's
    Calibre xRC rules (its LVS connectivity, the capacitance and resistance rules), their template
    setup commented out."""

    from flow.layout.calibre_pex import run_layout_pex as extract
    from flow.layout.calibre_pex import specialize

    work = (run_dir / "pex").resolve()
    work.mkdir(parents=True, exist_ok=True)
    lvs = specialize(
        KIT / "Calibre/RSF/lvs.tvf",
        work / "lvs.tvf",
        (
            (' tvf::LAYOUT PRIMARY "__TOP_CELL__"', " # set by FRIDA's control file: LAYOUT PRIMARY"),
            (" tvf::LAYOUT SYSTEM GDSII", " # set by FRIDA's control file: LAYOUT SYSTEM"),
        ),
    )
    xrc = specialize(
        KIT / "Calibre/RSF/xrc.tvf",
        work / "xrc.tvf",
        (("source $env(IHP_TECH)/Calibre/RSF/lvs.tvf", f"source {lvs}"),),
    )
    return extract(
        run_dir=work,
        gds_path=gds_path,
        layout_top=layout_top,
        output_stem=output_stem,
        deck=f'source "{xrc}"\n',
        environment={"IHP_TECH": str(KIT)},
        deck_sets=("ERC RESULTS",),  # the LVS rules set their own
    )
