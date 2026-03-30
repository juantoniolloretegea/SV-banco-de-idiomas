"""Laboratorio mínimo reproducible para el Documento 2 de la Colección I.
El bloque mantiene ejemplos continuos cosidos a las nueve posiciones del frame conversacional.
"""
from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass, asdict
from typing import Dict, List, Set

U = "U"

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

MAP_THETA = {"coherente": 0, "desvío": 1, "indeterminado": U}
MAP_PI = {"sin-pregunta": 0, "resuelta": 0, "bloqueada": 1, "indeterminada": U}
MAP_KAPPA = {"coherente": 0, "contradictoria": 1, "indeterminada": U}
MAP_ETA = {"completa": 0, "defectuosa": 1, "indeterminada": U}
MAP_GAMMA = {"alineada": 0, "bloqueada": 1, "indeterminada": U}
MAP_ALPHA = {"apropiada": 0, "inapropiada": 1, "indeterminada": U}
MAP_MU = {"sin-ambigüedad": 0, "cerrada": 0, "incompatible": 1, "indeterminada": U}
MAP_CHI = {"sin-solicitud": 0, "atendida": 0, "denegada": 1, "indeterminada": U}
MAP_PSI = {"en-curso": 0, "cerrado": 0, "bloqueado": 1, "indeterminado": U}


def _normalize_token(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _canonicalize_value(field_name: str, value: str, mapping: Dict[str, object]) -> str:
    by_normalized = {_normalize_token(key): key for key in mapping}
    probe = _normalize_token(value)
    if probe not in by_normalized:
        allowed = ", ".join(sorted(mapping.keys()))
        raise KeyError(f"{field_name}={value!r} fuera de dominio; valores canónicos admitidos: {allowed}")
    return by_normalized[probe]


def _canonicalize_observables(obs: Observables) -> Observables:
    return Observables(
        theta=_canonicalize_value("theta", obs.theta, MAP_THETA),
        pi=_canonicalize_value("pi", obs.pi, MAP_PI),
        kappa=_canonicalize_value("kappa", obs.kappa, MAP_KAPPA),
        eta=_canonicalize_value("eta", obs.eta, MAP_ETA),
        gamma=_canonicalize_value("gamma", obs.gamma, MAP_GAMMA),
        alpha=_canonicalize_value("alpha", obs.alpha, MAP_ALPHA),
        mu=_canonicalize_value("mu", obs.mu, MAP_MU),
        chi=_canonicalize_value("chi", obs.chi, MAP_CHI),
        psi=_canonicalize_value("psi", obs.psi, MAP_PSI),
    )


def i_nlp(obs: Observables) -> List[object]:
    obs = _canonicalize_observables(obs)
    return [
        MAP_THETA[obs.theta],
        MAP_PI[obs.pi],
        MAP_KAPPA[obs.kappa],
        MAP_ETA[obs.eta],
        MAP_GAMMA[obs.gamma],
        MAP_ALPHA[obs.alpha],
        MAP_MU[obs.mu],
        MAP_CHI[obs.chi],
        MAP_PSI[obs.psi],
    ]


def gamma_h_nlp(vector: List[object]) -> Dict[int, str]:
    out: Dict[int, str] = {}
    for idx, value in enumerate(vector, start=1):
        if value != U:
            continue
        support = H_NLP_SUPPORT.get(idx, set())
        if not support:
            out[idx] = "irreducible"
        elif len(support) == 1:
            out[idx] = "resoluble"
        else:
            out[idx] = "fronteriza"
    return out


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


def threshold(n: int) -> int:
    return (7 * n) // 9


def classify_frame_k3(vector: List[object]) -> str:
    n = len(vector)
    n1 = sum(value == 1 for value in vector)
    n0 = sum(value == 0 for value in vector)
    t = threshold(n)
    if n1 >= t:
        return "NO_APTO"
    if n0 >= t:
        return "APTO"
    return "INDETERMINADO"


def gobernable(vector: List[object]) -> bool:
    gamma = gamma_h_nlp(vector)
    return all(cls != "irreducible" for cls in gamma.values())


def summarize_case(name: str, obs: Observables) -> Dict[str, object]:
    vector = i_nlp(obs)
    gamma = gamma_h_nlp(vector)
    return {
        "caso": name,
        "observables": asdict(obs),
        "vector": vector,
        "gamma_h": gamma,
        "u_irr": [idx for idx, cls in gamma.items() if cls == "irreducible"],
        "k(v)": k_textura(vector),
        "bloques_u": bloques_u(vector),
        "gobernable": gobernable(vector),
        "clase_k3": classify_frame_k3(vector),
    }


def run_cases() -> Dict[str, object]:
    cases = {
        "ejemplo_A_pregunta_y_referente_abiertos": Observables(
            theta="coherente", pi="indeterminada", kappa="coherente", eta="completa",
            gamma="alineada", alpha="apropiada", mu="indeterminada",
            chi="sin-solicitud", psi="en-curso",
        ),
        "ejemplo_B_cierre_suficiente_del_frame": Observables(
            theta="coherente", pi="resuelta", kappa="coherente", eta="completa",
            gamma="alineada", alpha="apropiada", mu="cerrada",
            chi="sin-solicitud", psi="cerrado",
        ),
        "ejemplo_C_objetivo_y_clarificacion_abiertos": Observables(
            theta="coherente", pi="sin-pregunta", kappa="coherente", eta="completa",
            gamma="indeterminada", alpha="apropiada", mu="sin-ambigüedad",
            chi="indeterminada", psi="indeterminado",
        ),
        "caso_D_enunciado_complementable": Observables(
            theta="coherente", pi="sin-pregunta", kappa="coherente", eta="indeterminada",
            gamma="alineada", alpha="apropiada", mu="sin-ambigüedad",
            chi="sin-solicitud", psi="en-curso",
        ),
        "caso_E_contradiccion_material": Observables(
            theta="desvío", pi="bloqueada", kappa="contradictoria", eta="completa",
            gamma="bloqueada", alpha="inapropiada", mu="incompatible",
            chi="denegada", psi="bloqueado",
        ),
    }
    results = {name: summarize_case(name, obs) for name, obs in cases.items()}

    assert results["ejemplo_A_pregunta_y_referente_abiertos"]["vector"] == [0, U, 0, 0, 0, 0, U, 0, 0]
    assert results["ejemplo_A_pregunta_y_referente_abiertos"]["gamma_h"] == {2: "fronteriza", 7: "fronteriza"}
    assert results["ejemplo_A_pregunta_y_referente_abiertos"]["gobernable"] is True

    assert results["ejemplo_B_cierre_suficiente_del_frame"]["vector"] == [0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert results["ejemplo_B_cierre_suficiente_del_frame"]["gamma_h"] == {}
    assert results["ejemplo_B_cierre_suficiente_del_frame"]["gobernable"] is True

    assert results["ejemplo_C_objetivo_y_clarificacion_abiertos"]["vector"] == [0, 0, 0, 0, U, 0, 0, U, U]
    assert results["ejemplo_C_objetivo_y_clarificacion_abiertos"]["gamma_h"] == {5: "fronteriza", 8: "fronteriza", 9: "fronteriza"}
    assert results["ejemplo_C_objetivo_y_clarificacion_abiertos"]["gobernable"] is True

    assert results["caso_D_enunciado_complementable"]["gamma_h"] == {4: "resoluble"}
    assert results["caso_D_enunciado_complementable"]["gobernable"] is True

    assert results["caso_E_contradiccion_material"]["gamma_h"] == {}
    assert results["caso_E_contradiccion_material"]["gobernable"] is True
    assert results["caso_E_contradiccion_material"]["clase_k3"] == "NO_APTO"

    return {
        "resumen_global": {
            "casos": len(results),
            "casos_satisfactorios": len(results),
            "totalidad_transductor": True,
            "u_irr_global": 0,
            "poligonos_de_referencia": 3,
            "caso_E_clase_k3": "NO_APTO",
        },
        "casos": results,
    }

if __name__ == "__main__":
    payload = run_cases()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
