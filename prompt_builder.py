#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt‑Builder (Streamlit Web‑App) + Tests (ohne Streamlit‑Abhängigkeit) — mit Pflichtfeld‑Check, Mehrfachauswahl & Validierungen
======================================================================

Warum diese Version?
- Du wolltest die App **im Browser** nutzen. Streamlit liefert genau das – ohne `termios`/stdin‑Probleme.
- Die bisherigen **Unit‑Tests** bleiben erhalten und laufen via `python prompt_builder.py --test` (ohne Streamlit‑Import).

Start (Browser)
    python -m pip install streamlit
    streamlit run prompt_builder.py

Tests (kopf‑/browserlos)
    python prompt_builder.py --test

Hinweise
- Die Web‑Oberfläche führt dich durch: **Bereich → Rolle → Auftrag → Felder**.
- **Vor dem Generieren** wird eine **Checkliste fehlender Pflichtfelder** angezeigt; erst wenn alle ok sind, wird der Prompt erzeugt.
- **Mehrfachauswahl** für definierte Felder (z. B. *Thema*, *Rahmen*).
- **Validierungen** (z. B. `Dauer (Minuten)` muss Zahl > 0 sein).
- Export: **Download-Button** (TXT) und optional JSON‑Ansicht deiner Angaben.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
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
