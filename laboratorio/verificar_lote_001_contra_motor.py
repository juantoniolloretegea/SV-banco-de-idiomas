from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLING_SRC = ROOT.parent / "SV-motor-main" / "src"
if SIBLING_SRC.exists() and str(SIBLING_SRC) not in sys.path:
    sys.path.insert(0, str(SIBLING_SRC))

from sv_motor.algebra.nlp import Observables, run_agent  # type: ignore  # noqa: E402

LOT_PATH = ROOT / "idiomas" / "espanol" / "lotes" / "lote_001_inicial.json"
NORMALIZE = {"desvío": "desvio", "sin-ambigüedad": "sin-ambiguedad"}


def main() -> int:
    cases = json.loads(LOT_PATH.read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        obs = {k: NORMALIZE.get(str(v), str(v)) for k, v in case["observables"].items()}
        result = run_agent(Observables(**obs))
        rows.append({
            "id": case["id"],
            "k3_ok": result["k3"] == case["k3_esperado"],
            "politica_ok": result["politica"] == case["politica_esperada"],
        })
    payload = {
        "lote": LOT_PATH.name,
        "casos": rows,
        "dictamen": "APTO" if all(r["k3_ok"] and r["politica_ok"] for r in rows) else "NO_APTO",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["dictamen"] == "APTO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
