"""Laboratorio mínimo reproducible para el Documento 3 de la Colección I.

Agente Especializado en Lenguaje Natural para el Sistema Vectorial SV.

El laboratorio deriva el frame conversacional mínimo desde I_NLP,
construye la célula supervisora C_gob^9, compone la compuerta conservadora
T_NLP, clasifica globalmente en K_3 y emite la política de continuidad.
"""
from __future__ import annotations

import json
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Set

U = "U"
APTO = "APTO"
INDETERMINADO = "INDETERMINADO"
NO_APTO = "NO_APTO"
CERRAR_FRAME = "CERRAR_FRAME"
CONTINUAR_EN_WTK = "CONTINUAR_EN_W(T,k)"
PROPONER_FORK = "PROPONER_FORK"

# Horizonte mínimo heredado del Documento 2.
# Posiciones con U pueden ser:
# - irreducibles si el soporte está vacío,
# - resolubles si el soporte es singleton,
# - fronterizas si el soporte admite cierre en 0 y 1.
H_NLP_SUPPORT: Dict[int, Set[int]] = {
    1: {0, 1},
    2: {0, 1},
    3: {0, 1},
    4: {0},
    5: {0, 1},
    6: {0, 1},
    7: {0, 1},
    8: {0, 1},
    9: {0, 1},
}


@dataclass(frozen=True)
class Observables:
    theta: str
    pi: str
    kappa: str
    eta: str
    gamma: str
    alpha: str
    mu: str
    chi: str
    psi: str


def _strip_accents(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )


def canonicalize(label: str) -> str:
    raw = label.strip().lower()
    simplified = _strip_accents(raw)
    aliases = {
        "desvio": "desvío",
        "desvío": "desvío",
        "sin ambiguedad": "sin-ambigüedad",
        "sin ambigüedad": "sin-ambigüedad",
        "sin-ambiguedad": "sin-ambigüedad",
        "sin-ambigüedad": "sin-ambigüedad",
    }
    return aliases.get(raw, aliases.get(simplified, raw))


MAP_THETA = {"coherente": 0, "desvío": 1, "indeterminado": U}
MAP_PI = {"sin-pregunta": 0, "resuelta": 0, "bloqueada": 1, "indeterminada": U}
MAP_KAPPA = {"coherente": 0, "contradictoria": 1, "indeterminada": U}
MAP_ETA = {"completa": 0, "defectuosa": 1, "indeterminada": U}
MAP_GAMMA = {"alineada": 0, "bloqueada": 1, "indeterminada": U}
MAP_ALPHA = {"apropiada": 0, "inapropiada": 1, "indeterminada": U}
MAP_MU = {"sin-ambigüedad": 0, "cerrada": 0, "incompatible": 1, "indeterminada": U}
MAP_CHI = {"sin-solicitud": 0, "atendida": 0, "denegada": 1, "indeterminada": U}
MAP_PSI = {"en-curso": 0, "cerrado": 0, "bloqueado": 1, "indeterminado": U}


MAPPINGS = {
    "theta": MAP_THETA,
    "pi": MAP_PI,
    "kappa": MAP_KAPPA,
    "eta": MAP_ETA,
    "gamma": MAP_GAMMA,
    "alpha": MAP_ALPHA,
    "mu": MAP_MU,
    "chi": MAP_CHI,
    "psi": MAP_PSI,
}


def i_nlp(obs: Observables) -> List[object]:
    out: List[object] = []
    for field in ("theta", "pi", "kappa", "eta", "gamma", "alpha", "mu", "chi", "psi"):
        value = canonicalize(getattr(obs, field))
        mapping = MAPPINGS[field]
        if value not in mapping:
            raise ValueError(f"Valor fuera de dominio para {field}: {value!r}")
        out.append(mapping[value])
    return out


def gamma_h_nlp(vector: List[object], support: Dict[int, Set[int]] | None = None) -> Dict[int, str]:
    support = support or H_NLP_SUPPORT
    out: Dict[int, str] = {}
    for idx, value in enumerate(vector, start=1):
        if value != U:
            continue
        closure = support.get(idx, set())
        if not closure:
            out[idx] = "irreducible"
        elif len(closure) == 1:
            out[idx] = "resoluble"
        else:
            out[idx] = "fronteriza"
    return out


def supervisar_gobernabilidad(vector: List[object], support: Dict[int, Set[int]] | None = None) -> List[object]:
    gamma = gamma_h_nlp(vector, support)
    c_gob: List[object] = []
    for idx, value in enumerate(vector, start=1):
        if value == 1:
            c_gob.append(1)
            continue
        if value == 0:
            c_gob.append(0)
            continue
        status = gamma[idx]
        if status == "irreducible":
            c_gob.append(1)
        elif status == "resoluble":
            c_gob.append(0)
        else:
            c_gob.append(U)
    return c_gob


GATE_TABLE = {
    (0, 0): 0,
    (0, 1): 1,
    (0, U): U,
    (1, 0): 1,
    (1, 1): 1,
    (1, U): 1,
    (U, 0): U,
    (U, 1): 1,
    (U, U): U,
}


def componer_nlp(c_gob: List[object], c_frame: List[object]) -> List[object]:
    return [GATE_TABLE[(left, right)] for left, right in zip(c_gob, c_frame)]


def classify_global(a_nlp: List[object], u_irr: List[int]) -> str:
    if 1 in a_nlp:
        return NO_APTO
    if u_irr:
        return NO_APTO
    if U in a_nlp:
        return INDETERMINADO
    return APTO


def policy_for(clase: str) -> str:
    if clase == APTO:
        return CERRAR_FRAME
    if clase == INDETERMINADO:
        return CONTINUAR_EN_WTK
    return PROPONER_FORK


def threshold(n: int) -> int:
    return (7 * n) // 9


def k_textura(vector: List[object]) -> int:
    z = [1 if value == U else 0 for value in vector]
    if not z or all(v == 0 for v in z):
        return 0
    return sum(1 for i in range(len(z)) if z[i] != z[(i + 1) % len(z)])


def bloques_u(vector: List[object]) -> int:
    z = [1 if value == U else 0 for value in vector]
    if not any(z):
        return 0
    if all(z):
        return 1
    count = 0
    for i in range(len(z)):
        if z[i] == 1 and z[i - 1] == 0:
            count += 1
    return count


def fork_append_only(trajectory: List[Dict[str, object]], fork_from: int, new_state: Dict[str, object]) -> Dict[str, object]:
    base = [dict(item) for item in trajectory]
    branch = [dict(item) for item in trajectory[: fork_from + 1]]
    branch.append(new_state)
    return {
        "trayectoria_original": base,
        "trayectoria_fork": branch,
    }


def summarize_case(name: str, obs: Observables, support: Dict[int, Set[int]] | None = None) -> Dict[str, object]:
    vector = i_nlp(obs)
    gamma = gamma_h_nlp(vector, support)
    u_irr = [idx for idx, cls in gamma.items() if cls == "irreducible"]
    c_gob = supervisar_gobernabilidad(vector, support)
    a_nlp = componer_nlp(c_gob, vector)
    clase = classify_global(a_nlp, u_irr)
    politica = policy_for(clase)
    return {
        "caso": name,
        "observables": {key: canonicalize(value) for key, value in asdict(obs).items()},
        "C_frame^9": vector,
        "Gamma_H": gamma,
        "U_irr": u_irr,
        "C_gob^9": c_gob,
        "A_NLP": a_nlp,
        "kappa_3": clase,
        "politica": politica,
        "k(v)": k_textura(vector),
        "bloques_u": bloques_u(vector),
        "threshold": threshold(len(vector)),
    }


CASES: Dict[str, Observables] = {
    "caso_A_pregunta_y_referente_abiertos": Observables(
        theta="coherente", pi="indeterminada", kappa="coherente", eta="completa",
        gamma="alineada", alpha="apropiada", mu="indeterminada",
        chi="sin-solicitud", psi="en-curso",
    ),
    "caso_B_cierre_suficiente_del_frame": Observables(
        theta="coherente", pi="resuelta", kappa="coherente", eta="completa",
        gamma="alineada", alpha="apropiada", mu="cerrada",
        chi="sin-solicitud", psi="cerrado",
    ),
    "caso_C_objetivo_y_clarificacion_abiertos": Observables(
        theta="coherente", pi="sin-pregunta", kappa="coherente", eta="completa",
        gamma="indeterminada", alpha="apropiada", mu="sin-ambigüedad",
        chi="indeterminada", psi="indeterminado",
    ),
    "caso_D_contradiccion_material_persistente": Observables(
        theta="desvío", pi="bloqueada", kappa="contradictoria", eta="completa",
        gamma="bloqueada", alpha="inapropiada", mu="incompatible",
        chi="denegada", psi="bloqueado",
    ),
    "caso_E_puerta_limpia_hacia_inmunologia": Observables(
        theta="coherente", pi="resuelta", kappa="coherente", eta="completa",
        gamma="alineada", alpha="apropiada", mu="sin-ambigüedad",
        chi="sin-solicitud", psi="cerrado",
    ),
    "caso_F_huecos_linguisticos_salvables": Observables(
        theta="coherente", pi="indeterminada", kappa="coherente", eta="indeterminada",
        gamma="indeterminada", alpha="apropiada", mu="indeterminada",
        chi="indeterminada", psi="indeterminado",
    ),
    "caso_G_contradiccion_ambiguedad_y_denegacion": Observables(
        theta="desvío", pi="indeterminada", kappa="contradictoria", eta="defectuosa",
        gamma="indeterminada", alpha="inapropiada", mu="incompatible",
        chi="denegada", psi="bloqueado",
    ),
}


def run_cases() -> Dict[str, object]:
    results = {name: summarize_case(name, obs) for name, obs in CASES.items()}

    # Asertos de paridad con el manuscrito.
    assert results["caso_A_pregunta_y_referente_abiertos"]["C_frame^9"] == [0, U, 0, 0, 0, 0, U, 0, 0]
    assert results["caso_A_pregunta_y_referente_abiertos"]["Gamma_H"] == {2: "fronteriza", 7: "fronteriza"}
    assert results["caso_A_pregunta_y_referente_abiertos"]["kappa_3"] == INDETERMINADO

    assert results["caso_B_cierre_suficiente_del_frame"]["C_frame^9"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert results["caso_B_cierre_suficiente_del_frame"]["U_irr"] == []
    assert results["caso_B_cierre_suficiente_del_frame"]["kappa_3"] == APTO
    assert U not in results["caso_B_cierre_suficiente_del_frame"]["C_frame^9"]
    assert 1 not in results["caso_B_cierre_suficiente_del_frame"]["A_NLP"]

    assert results["caso_C_objetivo_y_clarificacion_abiertos"]["C_frame^9"] == [0, 0, 0, 0, U, 0, 0, U, U]
    assert results["caso_C_objetivo_y_clarificacion_abiertos"]["Gamma_H"] == {5: "fronteriza", 8: "fronteriza", 9: "fronteriza"}
    assert results["caso_C_objetivo_y_clarificacion_abiertos"]["kappa_3"] == INDETERMINADO

    assert results["caso_D_contradiccion_material_persistente"]["C_frame^9"] == [1, 1, 1, 0, 1, 1, 1, 1, 1]
    assert results["caso_D_contradiccion_material_persistente"]["kappa_3"] == NO_APTO
    assert results["caso_D_contradiccion_material_persistente"]["politica"] == PROPONER_FORK

    assert results["caso_E_puerta_limpia_hacia_inmunologia"]["kappa_3"] == APTO
    assert results["caso_E_puerta_limpia_hacia_inmunologia"]["politica"] == CERRAR_FRAME

    # Presencia de U en P2, P5, P7, P8, P9 y régimen indeterminado.
    assert results["caso_F_huecos_linguisticos_salvables"]["C_frame^9"] == [0, U, 0, U, U, 0, U, U, U]
    assert results["caso_F_huecos_linguisticos_salvables"]["kappa_3"] == INDETERMINADO

    assert results["caso_G_contradiccion_ambiguedad_y_denegacion"]["C_frame^9"] == [1, U, 1, 1, U, 1, 1, 1, 1]
    assert results["caso_G_contradiccion_ambiguedad_y_denegacion"]["kappa_3"] == NO_APTO
    assert results["caso_G_contradiccion_ambiguedad_y_denegacion"]["politica"] == PROPONER_FORK

    # Totalidad efectiva del clasificador K3.
    observed = {payload["kappa_3"] for payload in results.values()}
    assert observed == {APTO, INDETERMINADO, NO_APTO}

    # La compuerta preserva la severidad: nunca lava un 1.
    critical_pairs = [
        (0, 1), (1, 0), (1, 1), (1, U), (U, 1),
        (0, U), (U, 0), (U, U), (0, 0),
    ]
    severity_ok = all(GATE_TABLE[pair] == 1 for pair in [(0, 1), (1, 0), (1, 1), (1, U), (U, 1)])
    assert severity_ok

    # Append-only mínimo bajo fork: la trayectoria original no se reescribe.
    trajectory = [
        {"frame": "S0", "kappa_3": INDETERMINADO},
        {"frame": "S1", "kappa_3": INDETERMINADO},
        {"frame": "S2", "kappa_3": NO_APTO},
    ]
    forked = fork_append_only(trajectory, 1, {"frame": "S1_fork", "kappa_3": INDETERMINADO})
    assert forked["trayectoria_original"] == trajectory
    assert forked["trayectoria_fork"][:-1] == trajectory[:2]
    assert forked["trayectoria_fork"][-1]["frame"] == "S1_fork"

    return {
        "resumen_global": {
            "casos": len(results),
            "casos_satisfactorios": len(results),
            "k3_totalidad": True,
            "clases_observadas": sorted(observed),
            "compuerta_conservadora": True,
            "append_only": True,
            "pares_criticos_compuerta": [list(pair) for pair in critical_pairs],
        },
        "casos": results,
        "traza_fork_minima": forked,
    }


def main() -> None:
    payload = run_cases()
    out_path = Path(__file__).with_name("salida_casos_canonicos_doc3.json")
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
