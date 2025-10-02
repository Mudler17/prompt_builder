# prompt_builder_streamlit.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import textwrap, json, sys, argparse

# -------------------- Domain & Template --------------------
DOMAIN_TREE: Dict[str, Any] = {
    "Bereich": {
        "Elementarpädagogik": {
            "Rolle": {
                "Erzieher:in": {
                    "Auftrag": {
                        "Konzept Kinderaktivität": {
                            "Zielgruppe": ["U3", "3–4 Jahre", "5–6 Jahre", "Vorschule", "Gemischt", "Integrativ"],
                            "Thema": ["Sprache","Motorik","Sozialkompetenz","Natur & Umwelt","Musik","Mathematik","Naturwissenschaft","Kunst/Kreativität","Emotionen"],
                            "Rahmen": ["Drinnen","Draußen","Kleingruppe","Stationenlernen","Projektwoche","Tagesimpuls","Exkursion"],
                            "Dauer (Minuten)": "freitext",
                            "Materialien": "freitext",
                            "Besonderheiten": "freitext",
                        },
                        "Elterngespräch vorbereiten": {
                            "Anlass": ["Entwicklungsgespräch","Konfliktklärung","Förderempfehlung","Übergabe","Rückmeldung"],
                            "Kind-Profil (Stärken/Bedarfe)": "freitext",
                            "Ziel des Gesprächs": "freitext",
                            "Dauer (Minuten)": "freitext",
                        },
                        "Dokumentation Beobachtung": {
                            "Beobachtungsmethode": ["Anekdote","Lerngeschichte","Checkliste","Soziogramm","Zeit-Stichprobe","Target-Child","Narrativ"],
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Förderideen": "freitext",
                        },
                        "Elternabend planen": {
                            "Anlass": ["Kennenlernen","Sprachförderung","Mediennutzung","Übergänge","Partizipation"],
                            "Ziel des Gesprächs": "freitext",
                            "Dauer (Minuten)": "freitext",
                            "Materialien": "freitext",
                        },
                        "Portfolio-Eintrag erstellen": {
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Förderideen": "freitext",
                            "Materialien": "freitext",
                        },
                        "Übergang Kita-Schule vorbereiten": {
                            "Anlass": ["Schulreife","Elterninfo","Kooperation GS","Übergabegespräch"],
                            "Ziel des Gesprächs": "freitext",
                            "Förderideen": "freitext",
                            "Dauer (Minuten)": "freitext",
                        },
                        "Beobachtungsbogen auswerten": {
                            "Beobachtungsmethode": ["PERIK","Sismik","Seldak","Eigenes Raster"],
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Förderideen": "freitext",
                        },
                        "Tagesdokumentation erstellen": {
                            "Situation": "freitext",
                            "Materialien": "freitext",
                            "Besonderheiten": "freitext",
                        },
                        "Elternbrief verfassen": {
                            "Anlass": ["Projektstart","Projektabschluss","Feste/Feiern","Infos","Erinnerung"],
                            "Ziel des Gesprächs": "freitext",
                            "Materialien": "freitext"
                        },
                    }
                },
                "Praxisanleiter:in": {
                    "Auftrag": {
                        "Anleitung planen": {
                            "Kompetenzziel": [
                                "Beobachtungsbogen anwenden","Elterngespräche strukturieren","Dokumentation nach QM-Standard",
                                "Angebotsplanung mit Differenzierung","Situationsanalyse durchführen","Reflexionsgespräch moderieren"
                            ],
                            "Aufgabenbeschreibung": "freitext",
                            "Evaluationskriterium": [
                                "Checkliste vollständig","SMART-Ziel erreicht","Peer-Feedback positiv","Sicherheitsregeln eingehalten","Selbsteinschätzung stimmig","Lernziel sichtbar"
                            ],
                        },
                        "Feedbackgespräch führen": {
                            "Kompetenzziel": ["Selbstreflexion anregen","Zielvereinbarung formulieren","Beobachtungskriterien nutzen","Ich-Botschaften anwenden"],
                            "Aufgabenbeschreibung": "freitext",
                            "Evaluationskriterium": ["Reflexion nachvollziehbar","Konkret vereinbart","Nächstes Ziel definiert","Protokoll vollständig"],
                        },
                    }
                },
                "Kita-Leitung": {
                    "Auftrag": {
                        "Teammeeting vorbereiten": {
                            "Anlass": ["Jour fixe","Konzeptfortschritt","Fallbesprechung anonymisiert","Projektstart/-abschluss"],
                            "Ziel des Gesprächs": "freitext",
                            "Materialien": "freitext",
                        },
                        "Dienstplanung erstellen": {
                            "Rahmen": ["Regelbetrieb","Vertretung","Ferienbetrieb","Fortbildungstag"],
                            "Planungszeitraum (KW/Monat)": "freitext",
                            "Schichtmodell": ["Früh","Kernzeit","Spät","Randzeiten"],
                            "Mindestbesetzung je Zeitslot": "freitext",
                            "Abwesenheiten (Urlaub/Krankheit)": "freitext",
                            "Schließtage/Termine": "freitext",
                            "Restriktionen/Wünsche": "freitext",
                        },
                        "Konzept weiterentwickeln": {
                            "Thema": ["Partizipation","Inklusion","Sprachbildung","Bewegung","Medienbildung","Transitionen","Beobachtung/Dokumentation"],
                            "Konzeptbaustein(e)": ["Leitbild","Elternarbeit","Bildungsbereiche","Kooperation/Netzwerk","Qualitätssicherung","Räume/Materialien"],
                            "Ist-Stand": "freitext",
                            "Zielbild / Outcome": "freitext",
                            "Maßnahmen/Meilensteine": "freitext",
                            "Beteiligte": "freitext",
                            "Ressourcen": "freitext",
                        },
                        "Qualitätszirkel dokumentieren": {
                            "Beobachtungsmethode": ["Audit-Checkliste","Kollegiale Beratung","PDCA-Review"],
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Evaluationskriterium": ["Maßnahmen definiert","Standards eingehalten","Wirkung überprüfbar"],
                            "Maßnahmen/Follow-up": "freitext",
                        },
                        "Jahresplanung erstellen": {
                            "Rahmen": ["Projekte","Feste/Feiern","Elterntermine","Fortbildungen"],
                            "Planungszeitraum (Jahr/KW)": "freitext",
                            "Meilensteine": "freitext",
                            "Besonderheiten": "freitext",
                        },
                        "Krisenkommunikation vorbereiten": {
                            "Anlass": ["Störung Betrieb","Unfall anonymisiert","Pandemie-Maßnahme","IT-Ausfall"],
                            "Ziel des Gesprächs": "freitext",
                            "Kontaktkette/Verantwortlichkeiten": "freitext",
                            "Szenarien": "freitext",
                            "Checkliste": "freitext",
                            "Materialien": "freitext",
                        },
                    }
                },
            }
        }
    }
}

DOMAIN_META: Dict[str, Dict[str, Any]] = {
    # Erzieher:in
    "Konzept Kinderaktivität": {
        "required": ["Bereich","Rolle","Auftrag","Zielgruppe","Thema","Rahmen","Dauer (Minuten)"],
        "multi": ["Thema","Rahmen"],
        "numeric": {"Dauer (Minuten)": {"min": 1, "max": 600}},
    },
    "Elterngespräch vorbereiten": {
        "required": ["Bereich","Rolle","Auftrag","Anlass","Ziel des Gesprächs","Dauer (Minuten)"],
        "multi": [],
        "numeric": {"Dauer (Minuten)": {"min": 1, "max": 240}},
    },
    "Dokumentation Beobachtung": {
        "required": ["Bereich","Rolle","Auftrag","Beobachtungsmethode","Situation"],
        "multi": [],
        "numeric": {},
    },
    "Elternabend planen": {
        "required": ["Bereich","Rolle","Auftrag","Anlass","Ziel des Gesprächs","Dauer (Minuten)"],
        "multi": [],
        "numeric": {"Dauer (Minuten)": {"min": 15, "max": 240}},
    },
    "Portfolio-Eintrag erstellen": {
        "required": ["Bereich","Rolle","Auftrag","Situation","Interpretation"],
        "multi": [],
        "numeric": {},
    },
    "Übergang Kita-Schule vorbereiten": {
        "required": ["Bereich","Rolle","Auftrag","Anlass","Ziel des Gesprächs"],
        "multi": [],
        "numeric": {"Dauer (Minuten)": {"min": 1, "max": 240}},
    },
    "Beobachtungsbogen auswerten": {
        "required": ["Bereich","Rolle","Auftrag","Beobachtungsmethode","Interpretation"],
        "multi": [],
        "numeric": {},
    },
    "Tagesdokumentation erstellen": {
        "required": ["Bereich","Rolle","Auftrag","Situation"],
        "multi": [],
        "numeric": {},
    },
    "Elternbrief verfassen": {
        "required": ["Bereich","Rolle","Auftrag","Anlass"],
        "multi": [],
        "numeric": {},
    },
    # Praxisanleiter:in
    "Anleitung planen": {
        "required": ["Bereich","Rolle","Auftrag","Kompetenzziel","Aufgabenbeschreibung","Evaluationskriterium"],
        "multi": ["Kompetenzziel","Evaluationskriterium"],
        "numeric": {},
    },
    "Feedbackgespräch führen": {
        "required": ["Bereich","Rolle","Auftrag","Kompetenzziel","Aufgabenbeschreibung","Evaluationskriterium"],
        "multi": ["Kompetenzziel","Evaluationskriterium"],
        "numeric": {},
    },
    # Kita-Leitung
    "Teammeeting vorbereiten": {
        "required": ["Bereich","Rolle","Auftrag","Anlass","Ziel des Gesprächs"],
        "multi": [],
        "numeric": {},
    },
    "Dienstplanung erstellen": {
        "required": ["Bereich","Rolle","Auftrag","Rahmen","Planungszeitraum (KW/Monat)","Schichtmodell","Mindestbesetzung je Zeitslot"],
        "multi": ["Schichtmodell"],
        "numeric": {},
    },
    "Konzept weiterentwickeln": {
        "required": ["Bereich","Rolle","Auftrag","Thema","Zielbild / Outcome","Maßnahmen/Meilensteine"],
        "multi": ["Thema","Konzeptbaustein(e)"],
        "numeric": {},
    },
    "Qualitätszirkel dokumentieren": {
        "required": ["Bereich","Rolle","Auftrag","Beobachtungsmethode","Situation","Evaluationskriterium","Maßnahmen/Follow-up"],
        "multi": ["Evaluationskriterium"],
        "numeric": {},
    },
    "Jahresplanung erstellen": {
        "required": ["Bereich","Rolle","Auftrag","Rahmen","Planungszeitraum (Jahr/KW)"],
        "multi": [],
        "numeric": {},
    },
    "Krisenkommunikation vorbereiten": {
        "required": ["Bereich","Rolle","Auftrag","Anlass","Ziel des Gesprächs","Kontaktkette/Verantwortlichkeiten"],
        "multi": [],
        "numeric": {},
    },
}

PROMPT_TEMPLATE = textwrap.dedent("""
Rolle: {Rolle}
Bereich: {Bereich}
Auftrag: {Auftrag}

Kontext:
- Zielgruppe: {Zielgruppe}
- Thema: {Thema}
- Konzeptbaustein(e): {Konzeptbaustein(e)}
- Rahmen: {Rahmen}
- Planungszeitraum (KW/Monat): {Planungszeitraum (KW/Monat)}
- Planungszeitraum (Jahr/KW): {Planungszeitraum (Jahr/KW)}
- Schichtmodell: {Schichtmodell}
- Mindestbesetzung je Zeitslot: {Mindestbesetzung je Zeitslot}
- Abwesenheiten (Urlaub/Krankheit): {Abwesenheiten (Urlaub/Krankheit)}
- Schließtage/Termine: {Schließtage/Termine}
- Restriktionen/Wünsche: {Restriktionen/Wünsche}
- Dauer (Minuten): {Dauer (Minuten)}
- Materialien: {Materialien}
- Ressourcen: {Ressourcen}
- Besonderheiten: {Besonderheiten}
- Anlass: {Anlass}
- Kind-Profil (Stärken/Bedarfe): {Kind-Profil (Stärken/Bedarfe)}
- Ziel des Gesprächs: {Ziel des Gesprächs}
- Kontaktkette/Verantwortlichkeiten: {Kontaktkette/Verantwortlichkeiten}
- Beobachtungsmethode: {Beobachtungsmethode}
- Situation: {Situation}
- Ist-Stand: {Ist-Stand}
- Interpretation: {Interpretation}
- Maßnahmen/Meilensteine: {Maßnahmen/Meilensteine}
- Maßnahmen/Follow-up: {Maßnahmen/Follow-up}
- Beteiligte: {Beteiligte}
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
""").strip()

DEFAULT_KEYS = [
    "Rolle","Bereich","Auftrag","Zielgruppe","Thema","Konzeptbaustein(e)","Rahmen",
    "Planungszeitraum (KW/Monat)","Planungszeitraum (Jahr/KW)","Schichtmodell","Mindestbesetzung je Zeitslot",
    "Abwesenheiten (Urlaub/Krankheit)","Schließtage/Termine","Restriktionen/Wünsche",
    "Dauer (Minuten)","Materialien","Ressourcen","Besonderheiten","Anlass",
    "Kind-Profil (Stärken/Bedarfe)","Ziel des Gesprächs","Kontaktkette/Verantwortlichkeiten",
    "Beobachtungsmethode","Situation","Ist-Stand","Interpretation","Maßnahmen/Meilensteine","Maßnahmen/Follow-up",
    "Beteiligte","Förderideen","Kompetenzziel","Aufgabenbeschreibung","Evaluationskriterium"
]

# -------------------- Pure logic --------------------
@dataclass
class WizardState:
    selections: Dict[str, Any] = field(default_factory=dict)
    def to_preview_lines(self) -> List[str]:
        return [f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in self.selections.items()]
    def compose_prompt(self) -> str:
        data = {k: "" for k in DEFAULT_KEYS}
        for k, v in self.selections.items():
            data[k] = ", ".join(v) if isinstance(v, list) else v
        prompt = PROMPT_TEMPLATE
        for k in DEFAULT_KEYS:
            prompt = prompt.replace("{"+k+"}", data.get(k, ""))
        return prompt.strip()

def validate(selections: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    for core in ["Bereich","Rolle","Auftrag"]:
        if not selections.get(core):
            issues.append(f"Pflichtfeld fehlt: {core}")
    meta = DOMAIN_META.get(selections.get("Auftrag") or "", {})
    for key in meta.get("required", []):
        val = selections.get(key)
        if isinstance(val, list):
            if not val: issues.append(f"Pflichtfeld (Mehrfachauswahl) fehlt: {key}")
        else:
            if not val: issues.append(f"Pflichtfeld fehlt: {key}")
    for key, rng in meta.get("numeric", {}).items():
        raw = selections.get(key)
        if not raw: continue
        try:
            num = float(str(raw).replace(",", "."))
        except Exception:
            issues.append(f"{key}: muss eine Zahl sein"); continue
        if "min" in rng and num < rng["min"]: issues.append(f"{key}: muss ≥ {rng['min']} sein")
        if "max" in rng and num > rng["max"]: issues.append(f"{key}: muss ≤ {rng['max']} sein")
    return issues

def progress_ratio(selections: Dict[str, Any]) -> tuple[int,int]:
    meta = DOMAIN_META.get(selections.get("Auftrag",""), {})
    req = meta.get("required", [])
    if not req: return (0,0)
    done=0
    for k in req:
        v = selections.get(k)
        if isinstance(v, list):
            if v: done+=1
        else:
            if v: done+=1
    return (done, len(req))

# -------------------- Streamlit UI --------------------
def run_streamlit_app() -> None:
    import streamlit as st
    import streamlit.components.v1 as components

    st.set_page_config(page_title="Prompt-Builder", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
    <div style="border:2px solid #ef4444; background:#fee2e2; color:#991b1b; padding:12px 16px; border-radius:8px; font-weight:700; margin:12px 0;">
      ⚠️ Wichtig (Datenschutz): Keine personenbezogenen Daten eingeben und nicht so formulieren,
      dass ein Rückschluss auf ein bestimmtes Kind möglich ist.
    </div>
    """, unsafe_allow_html=True)
    st.title("🧭 Geführter Prompt-Builder — Elementarpädagogik")

    if "state" not in st.session_state:
        st.session_state.state = WizardState()
    state: WizardState = st.session_state.state

    with st.sidebar:
        st.subheader("⚙️ Optionen")
        d,t = progress_ratio(state.selections)
        st.progress((d/t) if t else 0.0)
        st.caption(f"Fortschritt Pflichtfelder: {d}/{t}" if t else "Noch kein Auftrag gewählt")
        st.markdown("---")
        if st.checkbox("Eingaben als JSON anzeigen"):
            st.json(state.selections)

    col_left, col_right = st.columns([2,1], gap="large")

    with col_left:
        st.subheader("Schritte")

        with st.container(border=True):
            st.markdown("**Zwischenstand**")
            if state.selections:
                st.write("\n".join("• "+line for line in state.to_preview_lines()))
            else:
                st.caption("Noch nichts erfasst.")

        state.selections.setdefault("Bereich","Elementarpädagogik")
        st.caption("Bereich: **Elementarpädagogik** (fest)")

        rollen = list(DOMAIN_TREE["Bereich"]["Elementarpädagogik"]["Rolle"].keys())
        sel_rolle = st.selectbox("Rolle", options=[""]+rollen,
                                 index=(rollen.index(state.selections.get("Rolle"))+1) if state.selections.get("Rolle") in rollen else 0)
        if sel_rolle != state.selections.get("Rolle"):
            state.selections["Rolle"] = sel_rolle or ""
            for k in list(state.selections.keys()):
                if k not in {"Bereich","Rolle","Auftrag"}: state.selections.pop(k, None)
            state.selections.pop("Auftrag", None)

        auftraege = list(DOMAIN_TREE["Bereich"]["Elementarpädagogik"]["Rolle"].get(state.selections.get("Rolle") or "", {}).get("Auftrag", {}).keys())
        sel_auftrag = st.selectbox("Auftrag", options=[""]+auftraege,
                                   index=(auftraege.index(state.selections.get("Auftrag"))+1) if state.selections.get("Auftrag") in auftraege else 0)
        if sel_auftrag != state.selections.get("Auftrag"):
            state.selections["Auftrag"] = sel_auftrag or ""
            for k in list(state.selections.keys()):
                if k not in {"Bereich","Rolle","Auftrag"}: state.selections.pop(k, None)

        leaf = {}
        if state.selections.get("Rolle") and state.selections.get("Auftrag"):
            leaf = DOMAIN_TREE["Bereich"]["Elementarpädagogik"]["Rolle"][state.selections["Rolle"]]["Auftrag"][state.selections["Auftrag"]]
        meta = DOMAIN_META.get(state.selections.get("Auftrag",""), {"multi":[],"required":[],"numeric":{}})
        sensitive = {"Kind-Profil (Stärken/Bedarfe)","Situation","Interpretation"}

        if leaf:
            st.markdown("---"); st.subheader("Details")
            for key, sub in leaf.items():
                if isinstance(sub, list):
                    options = sub
                    current = state.selections.get(key)
                    if key in meta.get("multi", []):
                        default = current if isinstance(current, list) else ([current] if current else [])
                        val = st.multiselect(key, options, default=default)
                        state.selections[key] = val
                        if key in meta.get("required", []) and not val:
                            st.caption("Pflichtfeld: bitte mindestens eine Option wählen.")
                    else:
                        idx = (options.index(current)+1) if isinstance(current, str) and current in options else 0
                        val = st.selectbox(key, options=[""]+options, index=idx)
                        state.selections[key] = val or ""
                        if key in meta.get("required", []) and not val:
                            st.caption("Pflichtfeld: bitte auswählen.")
                elif sub == "freitext":
                    is_long = any(t in key.lower() for t in ["beschreibung","material","besonder","situation","interpretation","förder","profil","ziel","maßnahmen","planungs"])
                    if key == "Dauer (Minuten)":
                        raw = st.text_input(key, value=str(state.selections.get(key, "")))
                        state.selections[key] = raw
                        rng = meta.get("numeric", {}).get(key)
                        if raw:
                            try:
                                num = float(str(raw).replace(",", "."))
                                if rng and (num < rng.get("min", -1e9) or num > rng.get("max", 1e9)):
                                    st.caption(f"Zahl außerhalb des gültigen Bereichs ({rng.get('min','?')}–{rng.get('max','?')}).")
                            except Exception:
                                st.caption("Bitte Zahl eingeben (z. B. 30).")
                        elif key in meta.get("required", []):
                            st.caption("Pflichtfeld: bitte ausfüllen.")
                    elif is_long:
                        val = st.text_area(key, value=state.selections.get(key,""), height=100)
                        state.selections[key] = val
                        if key in sensitive:
                            st.caption("Hinweis Datenschutz: bitte neutral/abstrahiert formulieren, keine personenbezogenen Details.")
                    else:
                        val = st.text_input(key, value=state.selections.get(key,""))
                        state.selections[key] = val
                        if key in sensitive:
                            st.caption("Hinweis Datenschutz: bitte neutral/abstrahiert formulieren, keine personenbezogenen Details.")

        st.markdown("---")
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("🔄 Zurücksetzen", use_container_width=True):
                st.session_state.state = WizardState(); st.rerun()
        with c2:
            preview_clicked = st.button("👁️ Vorschau", use_container_width=True)
        with c3:
            gen_clicked = st.button("✨ Prompt erzeugen", use_container_width=True)

    with col_right:
        st.subheader("Ergebnis")
        result_placeholder = st.empty()
        downloads_placeholder = st.container()

    want_output = preview_clicked or gen_clicked
    issues = validate(state.selections) if want_output else []
    if want_output and issues:
        st.error("Bitte folgende Punkte korrigieren, bevor der Prompt erzeugt wird:")
        st.write("\n".join("• "+m for m in issues))
    elif want_output:
        prompt_text = state.compose_prompt()
        result_placeholder.code(prompt_text)
        with downloads_placeholder:
            st.download_button("⬇️ TXT", data=prompt_text, file_name="prompt_output.txt", mime="text/plain")
            st.download_button("⬇️ JSON", data=json.dumps(state.selections, ensure_ascii=False, indent=2), file_name="prompt.json", mime="application/json")
            md = f"## Prompt\n\n````\n{prompt_text}\n````\n"
            st.download_button("⬇️ Markdown", data=md, file_name="prompt.md", mime="text/markdown")
            st.caption("Tipp: Im Code-Block oben gibt es einen Copy-Button. Falls dein Browser blockt, nutze den Fallback unten.")
            import streamlit.components.v1 as components
            components.html(f'''
            <div style="margin-top:8px">
              <textarea id="pb_copy" style="position:absolute; left:-9999px;">{prompt_text}</textarea>
              <button style="padding:6px 10px"
                onclick="const el=document.getElementById('pb_copy'); el.select(); document.execCommand('copy'); this.innerText='Kopiert!'; setTimeout(()=>this.innerText='In die Zwischenablage kopieren (Fallback)',1200);">
                In die Zwischenablage kopieren (Fallback)
              </button>
            </div>
            ''', height=40)

def run_tests() -> int:
    # leichte Smoke-Tests der Logik
    ws = WizardState(selections={"Rolle":"Erzieher:in","Bereich":"Elementarpädagogik","Auftrag":"Konzept Kinderaktivität"})
    assert "Auftrag: Konzept Kinderaktivität" in ws.compose_prompt()
    sel = {"Bereich":"Elementarpädagogik","Rolle":"Kita-Leitung","Auftrag":"Dienstplanung erstellen",
           "Rahmen":["Regelbetrieb"],"Planungszeitraum (KW/Monat)":"KW 41-44","Schichtmodell":["Früh"],"Mindestbesetzung je Zeitslot":"2"}
    assert not validate(sel)
    print("Tests ok."); return 0

def _run_cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args,_ = parser.parse_known_args()
    if args.test:
        sys.exit(run_tests())
    run_streamlit_app()

if __name__ == "__main__":
    _run_cli()
