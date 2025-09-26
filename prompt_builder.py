#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt‑Builder (Streamlit Web‑App) — mit Pflichtfeld‑Check, Mehrfachauswahl & Validierungen
=========================================================================================

✅ Browserfähig, kein stdin/termios nötig. 
✅ Funktioniert lokal und in Hosting‑Umgebungen (Streamlit Cloud / HF Spaces).
✅ Enthält eingebaute Tests, die *ohne* Streamlit importierbar sind.

Start lokal (Browser)
    python -m pip install streamlit
    streamlit run prompt_builder.py

Tests (ohne Browser)
    python prompt_builder.py --test

Hinweise
- Menü: **Bereich → Rolle → Auftrag → Felder** (dynamisch)
- **Vor dem Generieren**: Checkliste fehlender Pflichtfelder; erst bei „grün“ wird der Prompt erzeugt.
- **Mehrfachauswahl** (aktuell bei *Thema*, *Rahmen*)
- **Validierungen** (z. B. `Dauer (Minuten)` muss Zahl im gültigen Bereich sein)

Deployment‑Hinweis
- Erstelle eine `requirements.txt` mit:
    streamlit>=1.33
- Lege diese Datei und `prompt_builder.py` in dein Repo. In Streamlit Cloud als Hauptdatei `prompt_builder.py` wählen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import sys
import textwrap
from pathlib import Path
import argparse
import json

# ------------------------------------------------------------
# 1) KONFIGURATION (Domainbaum & Template)
# ------------------------------------------------------------

DOMAIN_TREE: Dict[str, Any] = {
    "Bereich": {
        "Elementarpädagogik": {
            "Rolle": {
                "Erzieherin": {
                    "Auftrag": {
                        "Konzept Kinderaktivität": {
                            "Zielgruppe": ["3–4 Jahre", "5–6 Jahre", "Gemischt"],
                            "Thema": ["Sprache", "Motorik", "Sozialkompetenz", "Natur & Umwelt"],
                            "Rahmen": ["Drinnen", "Draußen", "Projektwoche", "Tagesimpuls"],
                            "Dauer (Minuten)": "freitext",
                            "Materialien": "freitext",
                            "Besonderheiten": "freitext",
                        },
                        "Elterngespräch vorbereiten": {
                            "Anlass": ["Entwicklungsgespräch", "Konfliktklärung", "Förderempfehlung"],
                            "Kind-Profil (Stärken/Bedarfe)": "freitext",
                            "Ziel des Gesprächs": "freitext",
                            "Dauer (Minuten)": "freitext",
                        },
                        "Dokumentation Beobachtung": {
                            "Beobachtungsmethode": ["Anekdote", "Lerngeschichte", "Checkliste"],
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Förderideen": "freitext",
                        },
                    },
                },
                "Praxisanleiter:in": {
                    "Auftrag": {
                        "Anleitung planen": {
                            "Kompetenzziel": "freitext",
                            "Aufgabenbeschreibung": "freitext",
                            "Evaluationskriterium": "freitext",
                        }
                    }
                },
            }
        },
        # Platzhalter für spätere Erweiterungen
        "Schule": {},
        "Jugendhilfe": {},
    }
}

PROMPT_TEMPLATE = textwrap.dedent(
    """
    Rolle: {Rolle}
    Bereich: {Bereich}
    Auftrag: {Auftrag}

    Kontext:
    - Zielgruppe: {Zielgruppe}
    - Thema: {Thema}
    - Rahmen: {Rahmen}
    - Dauer (Minuten): {Dauer (Minuten)}
    - Materialien: {Materialien}
    - Besonderheiten: {Besonderheiten}
    - Anlass: {Anlass}
    - Kind-Profil (Stärken/Bedarfe): {Kind-Profil (Stärken/Bedarfe)}
    - Ziel des Gesprächs: {Ziel des Gesprächs}
    - Beobachtungsmethode: {Beobachtungsmethode}
    - Situation: {Situation}
    - Interpretation: {Interpretation}
    - Förderideen: {Förderideen}
    - Kompetenzziel: {Kompetenzziel}
    - Aufgabenbeschreibung: {Aufgabenbeschreibung}
    - Evaluationskriterium: {Evaluationskriterium}

    Aufgabe:
    Erstelle auf Basis der Angaben eine strukturierte Ausarbeitung (max. 700 Wörter) mit:
    1) Ziel & Begründung (beobachtbare Kriterien)
    2) Ablauf/Phasen (Minutenangaben, Methoden, Differenzierung)
    3) Materialien & Raum
    4) Beobachtung & Dokumentation
    5) Reflexionsfragen
    Schreibe klar, prägnant, handlungsorientiert.
    """
).strip()

DEFAULT_KEYS = [
    "Rolle","Bereich","Auftrag","Zielgruppe","Thema","Rahmen","Dauer (Minuten)",
    "Materialien","Besonderheiten","Anlass","Kind-Profil (Stärken/Bedarfe)",
    "Ziel des Gesprächs","Beobachtungsmethode","Situation","Interpretation",
    "Förderideen","Kompetenzziel","Aufgabenbeschreibung","Evaluationskriterium"
]

# Meta-Definitionen pro Auftrag: Pflichtfelder, Multi-Select-Keys, Numeric-Constraints
DOMAIN_META: Dict[str, Dict[str, Any]] = {
    "Konzept Kinderaktivität": {
        "required": ["Bereich", "Rolle", "Auftrag", "Zielgruppe", "Thema", "Rahmen", "Dauer (Minuten)"],
        "multi": ["Thema", "Rahmen"],
        "numeric": {"Dauer (Minuten)": {"min": 1, "max": 600}},
    },
    "Elterngespräch vorbereiten": {
        "required": ["Bereich", "Rolle", "Auftrag", "Anlass", "Ziel des Gesprächs", "Dauer (Minuten)"],
        "multi": [],
        "numeric": {"Dauer (Minuten)": {"min": 1, "max": 240}},
    },
    "Dokumentation Beobachtung": {
        "required": ["Bereich", "Rolle", "Auftrag", "Beobachtungsmethode", "Situation"],
        "multi": [],
        "numeric": {},
    },
    "Anleitung planen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Kompetenzziel", "Aufgabenbeschreibung", "Evaluationskriterium"],
        "multi": [],
        "numeric": {},
    },
}

# ------------------------------------------------------------
# 2) MODELL & HILFSFUNKTIONEN (Streamlit‑agnostisch)
# ------------------------------------------------------------

@dataclass
class WizardState:
    selections: Dict[str, Any] = field(default_factory=dict)

    def to_preview_lines(self) -> List[str]:
        return [f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in self.selections.items()]

    def compose_prompt(self) -> str:
        data = {k: "" for k in DEFAULT_KEYS}
        for k, v in self.selections.items():
            data[k] = ", ".join(v) if isinstance(v, list) else v
        try:
            return PROMPT_TEMPLATE.format(**data).strip()
        except KeyError:
            prompt = PROMPT_TEMPLATE
            for k in DEFAULT_KEYS:
                prompt = prompt.replace("{" + k + "}", data.get(k, ""))
            return prompt.strip()


def build_steps_from_node(node: Any) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []
    if isinstance(node, dict):
        for key, sub in node.items():
            if isinstance(sub, dict):
                steps.append({"key": key, "kind": "choice", "options": list(sub.keys())})
            elif isinstance(sub, list):
                steps.append({"key": key, "kind": "choice", "options": sub})
            elif sub == "freitext":
                steps.append({"key": key, "kind": "text"})
    return steps


def validate(selections: Dict[str, Any]) -> List[str]:
    """Gibt eine Liste von Fehler-/Hinweistexten zurück. Leere Liste ⇒ alles ok."""
    issues: List[str] = []
    # Kernpflichten
    for core in ["Bereich", "Rolle", "Auftrag"]:
        if not selections.get(core):
            issues.append(f"Pflichtfeld fehlt: {core}")
    auftrag = selections.get("Auftrag")
    meta = DOMAIN_META.get(auftrag, None)
    if meta:
        # Pflichtfelder
        for key in meta.get("required", []):
            val = selections.get(key)
            if isinstance(val, list):
                if not val:
                    issues.append(f"Pflichtfeld (Mehrfachauswahl) fehlt: {key}")
            else:
                if val in (None, ""):
                    issues.append(f"Pflichtfeld fehlt: {key}")
        # Numerik
        for key, rule in meta.get("numeric", {}).items():
            raw = selections.get(key)
            if raw in (None, ""):
                continue
            try:
                num = float(str(raw).replace(",", "."))
            except Exception:
                issues.append(f"{key}: muss eine Zahl sein")
                continue
            if "min" in rule and num < rule["min"]:
                issues.append(f"{key}: muss ≥ {rule['min']} sein")
            if "max" in rule and num > rule["max"]:
                issues.append(f"{key}: muss ≤ {rule['max']} sein")
    return issues


# ------------------------------------------------------------
# 3) STREAMLIT‑UI (wird nur aufgerufen, wenn unter Streamlit ausgeführt)
# ------------------------------------------------------------

def run_streamlit_app() -> None:
    import streamlit as st

    st.set_page_config(page_title="Prompt‑Builder", page_icon="🧭", layout="wide")
    st.title("🧭 Geführter Prompt‑Builder")
    st.caption("Bereich → Rolle → Auftrag → Felder. Export als Text oder JSON.")

    if "state" not in st.session_state:
        st.session_state.state = WizardState()

    state: WizardState = st.session_state.state

    # --- Spaltenlayout
    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        st.subheader("Schritte")
        # 1) Bereich
        bereiche = list(DOMAIN_TREE.get("Bereich", {}).keys())
        sel_bereich = st.selectbox(
            "Bereich",
            options=[""] + bereiche,
            index=(bereiche.index(state.selections.get("Bereich")) + 1) if state.selections.get("Bereich") in bereiche else 0,
        )
        if sel_bereich != state.selections.get("Bereich"):
            state.selections["Bereich"] = sel_bereich or ""
            for k in ["Rolle", "Auftrag"]:
                state.selections.pop(k, None)
            # Unterfelder leeren
            for k in list(state.selections.keys()):
                if k not in {"Bereich", "Rolle", "Auftrag"}:
                    state.selections.pop(k, None)

        # 2) Rolle
        rollen = []
        if state.selections.get("Bereich"):
            rollen = list(DOMAIN_TREE["Bereich"][state.selections["Bereich"]].get("Rolle", {}).keys())
        sel_rolle = st.selectbox(
            "Rolle",
            options=[""] + rollen,
            index=(rollen.index(state.selections.get("Rolle")) + 1) if state.selections.get("Rolle") in rollen else 0,
        )
        if sel_rolle != state.selections.get("Rolle"):
            state.selections["Rolle"] = sel_rolle or ""
            for k in ["Auftrag"]:
                state.selections.pop(k, None)
            for k in list(state.selections.keys()):
                if k not in {"Bereich", "Rolle", "Auftrag"}:
                    state.selections.pop(k, None)

        # 3) Auftrag
        auftraege = []
        if state.selections.get("Bereich") and state.selections.get("Rolle"):
            auftraege = list(
                DOMAIN_TREE["Bereich"][state.selections["Bereich"]]["Rolle"][state.selections["Rolle"]]
                .get("Auftrag", {})
                .keys()
            )
        sel_auftrag = st.selectbox(
            "Auftrag",
            options=[""] + auftraege,
            index=(auftraege.index(state.selections.get("Auftrag")) + 1) if state.selections.get("Auftrag") in auftraege else 0,
        )
        if sel_auftrag != state.selections.get("Auftrag"):
            state.selections["Auftrag"] = sel_auftrag or ""
            for k in list(state.selections.keys()):
                if k not in {"Bereich", "Rolle", "Auftrag"}:
                    state.selections.pop(k, None)

        # 4) Felder (Blattebene)
        leaf_node: Dict[str, Any] = {}
        if state.selections.get("Bereich") and state.selections.get("Rolle") and state.selections.get("Auftrag"):
            leaf_node = (
                DOMAIN_TREE["Bereich"][state.selections["Bereich"]]["Rolle"][state.selections["Rolle"]]["Auftrag"][state.selections["Auftrag"]]
            )

        meta = DOMAIN_META.get(state.selections.get("Auftrag", ""), {"multi": [], "required": [], "numeric": {}})

        if leaf_node:
            st.markdown("---")
            st.subheader("Details")
            for key, sub in leaf_node.items():
                if isinstance(sub, list):
                    opts = sub
                    current = state.selections.get(key)
                    if key in meta.get("multi", []):
                        preselect = current if isinstance(current, list) else ([current] if current else [])
                        val = st.multiselect(key, options=opts, default=preselect)
                        state.selections[key] = val
                    else:
                        idx = (opts.index(current) + 1) if isinstance(current, str) and current in opts else 0
                        val = st.selectbox(key, options=[""] + opts, index=idx)
                        state.selections[key] = val or ""
                elif sub == "freitext":
                    is_long = any(token in key.lower() for token in [
                        "beschreibung", "material", "besonder", "situation", "interpretation", "förder", "profil", "ziel"
                    ])
                    if key == "Dauer (Minuten)":
                        raw = st.text_input(key, value=str(state.selections.get(key, "")))
                        state.selections[key] = raw
                    elif is_long:
                        val = st.text_area(key, value=state.selections.get(key, ""), height=100)
                        state.selections[key] = val
                    else:
                        val = st.text_input(key, value=state.selections.get(key, ""))
                        state.selections[key] = val

        st.markdown("---")
        colA, colB, colC = st.columns([1, 1, 1])
        with colA:
            if st.button("🔄 Zurücksetzen", use_container_width=True):
                st.session_state.state = WizardState()
                st.rerun()
        with colB:
            preview_clicked = st.button("👁️ Vorschau", use_container_width=True)
        with colC:
            gen_clicked = st.button("✨ Prompt erzeugen", use_container_width=True)

    with col_right:
        st.subheader("Zwischenstand")
        if state.selections:
            st.write("\n".join(f"• {line}" for line in state.to_preview_lines()))
        else:
            st.caption("Noch nichts erfasst.")
        st.markdown("---")
        show_json = st.checkbox("Eingaben als JSON anzeigen")
        if show_json:
            st.json(state.selections)

    # Validierung & Ergebnis
    want_output = preview_clicked or gen_clicked
    issues = validate(state.selections) if want_output else []

    if want_output and issues:
        st.error("Bitte folgende Punkte korrigieren, bevor der Prompt erzeugt wird:")
        st.write("\n".join(f"• {msg}" for msg in issues))
    elif want_output:
        prompt_text = state.compose_prompt()
        st.markdown("## Ergebnis")
        st.code(prompt_text)
        st.download_button(
            "⬇️ Als TXT herunterladen",
            data=prompt_text,
            file_name="prompt_output.txt",
            mime="text/plain",
        )


# ------------------------------------------------------------
# 4) TESTS (ohne Streamlit‑Import)
# ------------------------------------------------------------

def _test_compose_prompt_minimal() -> None:
    ws = WizardState(selections={"Rolle": "Erzieherin", "Bereich": "Elementarpädagogik", "Auftrag": "Konzept Kinderaktivität"})
    out = ws.compose_prompt()
    assert "Rolle: Erzieherin" in out
    assert "Bereich: Elementarpädagogik" in out
    assert "Auftrag: Konzept Kinderaktivität" in out


def _test_compose_prompt_full_fields() -> None:
    ws = WizardState(selections={
        "Rolle": "Praxisanleiter:in",
        "Bereich": "Elementarpädagogik",
        "Auftrag": "Anleitung planen",
        "Kompetenzziel": "Beobachtungsbogen anwenden",
        "Aufgabenbeschreibung": "Kurzanleitung für Praktikant:in",
        "Evaluationskriterium": "Checkliste vollständig",
    })
    out = ws.compose_prompt()
    assert "Kompetenzziel: Beobachtungsbogen anwenden" in out
    assert "Evaluationskriterium: Checkliste vollständig" in out


def _test_domain_tree_structure() -> None:
    assert "Bereich" in DOMAIN_TREE
    assert "Elementarpädagogik" in DOMAIN_TREE["Bereich"]
    assert "Rolle" in DOMAIN_TREE["Bereich"]["Elementarpädagogik"]

# weitere sinnvolle Tests

def _test_missing_fields_blank() -> None:
    ws = WizardState(selections={"Rolle": "Erzieherin"})
    out = ws.compose_prompt()
    assert "Rolle: Erzieherin" in out and "Bereich:" in out


def _test_multiline_freetext() -> None:
    ws = WizardState(selections={
        "Rolle": "Erzieherin",
        "Bereich": "Elementarpädagogik",
        "Auftrag": "Konzept Kinderaktivität",
        "Materialien": "Papier\nStifte\nSchere",
    })
    out = ws.compose_prompt()
    assert "Papier" in out and "Stifte" in out and "Schere" in out


def _test_build_steps_leaf_fields() -> None:
    node = DOMAIN_TREE["Bereich"]["Elementarpädagogik"]["Rolle"]["Erzieherin"]["Auftrag"]["Konzept Kinderaktivität"]
    steps = build_steps_from_node(node)
    keys = [s["key"] for s in steps]
    for k in ["Zielgruppe", "Thema", "Rahmen", "Dauer (Minuten)"]:
        assert k in keys


def _test_validate_core_and_numeric() -> None:
    sel = {"Bereich": "Elementarpädagogik", "Rolle": "Erzieherin", "Auftrag": "Konzept Kinderaktivität", "Dauer (Minuten)": "0"}
    issues = validate(sel)
    assert any("Dauer (Minuten): muss ≥" in m for m in issues)


def _test_validate_required_missing() -> None:
    sel = {"Bereich": "Elementarpädagogik", "Rolle": "Erzieherin", "Auftrag": "Konzept Kinderaktivität"}
    issues = validate(sel)
    assert any("Zielgruppe" in m for m in issues) and any("Thema" in m for m in issues)


def _test_multiselect_storage() -> None:
    sel = {"Bereich": "Elementarpädagogik", "Rolle": "Erzieherin", "Auftrag": "Konzept Kinderaktivität", "Thema": ["Sprache", "Motorik"], "Rahmen": ["Drinnen"], "Zielgruppe": "3–4 Jahre", "Dauer (Minuten)": "30"}
    issues = validate(sel)
    assert not issues
    ws = WizardState(selections=sel)
    out = ws.compose_prompt()
    assert "Thema: Sprache, Motorik" in out and "Rahmen: Drinnen" in out


def run_tests() -> int:
    tests = [
        _test_compose_prompt_minimal,
        _test_compose_prompt_full_fields,
        _test_domain_tree_structure,
        _test_missing_fields_blank,
        _test_multiline_freetext,
        _test_build_steps_leaf_fields,
        _test_validate_core_and_numeric,
        _test_validate_required_missing,
        _test_multiselect_storage,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {e}")
            failures += 1
    total = len(tests)
    print(f"Tests: {total}, Failures: {failures}, Passed: {total - failures}")
    return failures


# ------------------------------------------------------------
# 5) ENTRY POINT — streamlit‑freundlich
# ------------------------------------------------------------

def _run_cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args, _ = parser.parse_known_args()
    if args.test:
        sys.exit(run_tests())
    # Wenn nicht Test: versuche, Streamlit‑App direkt zu starten (wenn unter Streamlit ausgeführt)
    try:
        import streamlit as st  # noqa: F401
        run_streamlit_app()
    except Exception as e:
        # Fallback: Hinweis im Terminal
        print("Dieses Modul ist für Streamlit gedacht. Starte die Web‑App mit:\n\n    streamlit run prompt_builder.py\n\nOder führe Tests aus mit:\n\n    python prompt_builder.py --test\n")
        # Zusätzlich Fehlerausgabe, falls in Hosting‑Logs hilfreich:
        print(f"[Info] Streamlit konnte nicht gestartet werden: {e}")


if __name__ == "__main__":
    _run_cli()
