# app.py
from __future__ import annotations
from flask import Flask, render_template_string, request, jsonify
import json
import textwrap

app = Flask(__name__)

# ---------- DOMAIN / META ----------
DOMAIN_TREE = {
    "Bereich": {
        "Elementarpädagogik": {
            "Rolle": {
                "Erzieher:in": {
                    "Auftrag": {
                        "Konzept Kinderaktivität": {
                            "Zielgruppe": ["U3", "3–4 Jahre", "5–6 Jahre", "Vorschule", "Gemischt", "Integrativ"],
                            "Thema": ["Sprache", "Motorik", "Sozialkompetenz", "Natur & Umwelt",
                                      "Musik", "Mathematik", "Naturwissenschaft", "Kunst/Kreativität", "Emotionen"],
                            "Rahmen": ["Drinnen", "Draußen", "Kleingruppe", "Stationenlernen",
                                       "Projektwoche", "Tagesimpuls", "Exkursion"],
                            "Dauer (Minuten)": "freitext",
                            "Materialien": "freitext",
                            "Besonderheiten": "freitext",
                        },
                        "Elterngespräch vorbereiten": {
                            "Anlass": ["Entwicklungsgespräch", "Konfliktklärung", "Förderempfehlung", "Übergabe", "Rückmeldung"],
                            "Kind-Profil (Stärken/Bedarfe)": "freitext",
                            "Ziel des Gesprächs": "freitext",
                            "Dauer (Minuten)": "freitext",
                        },
                        "Dokumentation Beobachtung": {
                            "Beobachtungsmethode": ["Anekdote", "Lerngeschichte", "Checkliste",
                                                    "Soziogramm", "Zeit-Stichprobe", "Target-Child", "Narrativ"],
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Förderideen": "freitext",
                        },
                        "Elternabend planen": {
                            "Anlass": ["Kennenlernen", "Sprachförderung", "Mediennutzung", "Übergänge", "Partizipation"],
                            "Ziel des Gesprächs": "freitext",
                            "Dauer (Minuten)": "freitext",
                            "Materialien": "freitext",
                        },
                        "Portfolio-Eintrag erstellen": {
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Förderideen": "freitext",
                            "Materialien": "freitext"
                        },
                        "Übergang Kita-Schule vorbereiten": {
                            "Anlass": ["Schulreife", "Elterninfo", "Kooperation GS", "Übergabegespräch"],
                            "Ziel des Gesprächs": "freitext",
                            "Förderideen": "freitext",
                            "Dauer (Minuten)": "freitext"
                        },
                        "Beobachtungsbogen auswerten": {
                            "Beobachtungsmethode": ["PERIK", "Sismik", "Seldak", "Eigenes Raster"],
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Förderideen": "freitext"
                        },
                        "Tagesdokumentation erstellen": {
                            "Situation": "freitext",
                            "Materialien": "freitext",
                            "Besonderheiten": "freitext"
                        },
                        "Elternbrief verfassen": {
                            "Anlass": ["Projektstart", "Projektabschluss", "Feste/Feiern", "Infos", "Erinnerung"],
                            "Ziel des Gesprächs": "freitext",
                            "Materialien": "freitext"
                            # (keine Dauer hier)
                        }
                    }
                },
                "Praxisanleiter:in": {
                    "Auftrag": {
                        "Anleitung planen": {
                            "Kompetenzziel": [
                                "Beobachtungsbogen anwenden", "Elterngespräche strukturieren",
                                "Dokumentation nach QM-Standard", "Angebotsplanung mit Differenzierung",
                                "Situationsanalyse durchführen", "Reflexionsgespräch moderieren"
                            ],
                            "Aufgabenbeschreibung": "freitext",
                            "Evaluationskriterium": [
                                "Checkliste vollständig", "SMART-Ziel erreicht",
                                "Peer-Feedback positiv", "Sicherheitsregeln eingehalten",
                                "Selbsteinschätzung stimmig", "Lernziel sichtbar"
                            ]
                        },
                        "Feedbackgespräch führen": {
                            "Kompetenzziel": ["Selbstreflexion anregen", "Zielvereinbarung formulieren",
                                              "Beobachtungskriterien nutzen", "Ich-Botschaften anwenden"],
                            "Aufgabenbeschreibung": "freitext",
                            "Evaluationskriterium": ["Reflexion nachvollziehbar", "Konkret vereinbart",
                                                     "Nächstes Ziel definiert", "Protokoll vollständig"]
                        }
                    }
                },
                "Kita-Leitung": {
                    "Auftrag": {
                        "Teammeeting vorbereiten": {
                            "Anlass": ["Jour fixe", "Konzeptfortschritt", "Fallbesprechung anonymisiert", "Projektstart/-abschluss"],
                            "Ziel des Gesprächs": "freitext",
                            "Dauer (Minuten)": "freitext",
                            "Materialien": "freitext"
                        },
                        "Dienstplanung erstellen": {
                            "Rahmen": ["Regelbetrieb", "Vertretung", "Ferienbetrieb", "Fortbildungstag"],
                            "Planungszeitraum (KW/Monat)": "freitext",
                            "Schichtmodell": ["Früh", "Kernzeit", "Spät", "Randzeiten"],
                            "Mindestbesetzung je Zeitslot": "freitext",
                            "Abwesenheiten (Urlaub/Krankheit)": "freitext",
                            "Schließtage/Termine": "freitext",
                            "Restriktionen/Wünsche": "freitext"
                        },
                        "Konzept weiterentwickeln": {
                            "Thema": ["Partizipation", "Inklusion", "Sprachbildung", "Bewegung",
                                      "Medienbildung", "Transitionen", "Beobachtung/Dokumentation"],
                            "Konzeptbaustein(e)": ["Leitbild", "Elternarbeit", "Bildungsbereiche", "Kooperation/Netzwerk",
                                                   "Qualitätssicherung", "Räume/Materialien"],
                            "Ist-Stand": "freitext",
                            "Zielbild / Outcome": "freitext",
                            "Maßnahmen/Meilensteine": "freitext",
                            "Beteiligte": "freitext",
                            "Ressourcen": "freitext"
                        },
                        "Qualitätszirkel dokumentieren": {
                            "Beobachtungsmethode": ["Audit-Checkliste", "Kollegiale Beratung", "PDCA-Review"],
                            "Situation": "freitext",
                            "Interpretation": "freitext",
                            "Evaluationskriterium": ["Maßnahmen definiert", "Standards eingehalten", "Wirkung überprüfbar"],
                            "Maßnahmen/Follow-up": "freitext"
                        },
                        "Jahresplanung erstellen": {
                            "Rahmen": ["Projekte", "Feste/Feiern", "Elterntermine", "Fortbildungen"],
                            "Planungszeitraum (Jahr/KW)": "freitext",
                            "Meilensteine": "freitext",
                            "Besonderheiten": "freitext"
                        },
                        "Krisenkommunikation vorbereiten": {
                            "Anlass": ["Störung Betrieb", "Unfall anonymisiert", "Pandemie-Maßnahme", "IT-Ausfall"],
                            "Ziel des Gesprächs": "freitext",
                            "Kontaktkette/Verantwortlichkeiten": "freitext",
                            "Szenarien": "freitext",
                            "Checkliste": "freitext",
                            "Materialien": "freitext"
                        }
                    }
                }
            }
        }
    }
}

DOMAIN_META = {
    # Erzieher:in
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
    "Elternabend planen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Anlass", "Ziel des Gesprächs", "Dauer (Minuten)"],
        "multi": [],
        "numeric": {"Dauer (Minuten)": {"min": 15, "max": 240}},
    },
    "Portfolio-Eintrag erstellen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Situation", "Interpretation"],
        "multi": [],
        "numeric": {},
    },
    "Übergang Kita-Schule vorbereiten": {
        "required": ["Bereich", "Rolle", "Auftrag", "Anlass", "Ziel des Gesprächs"],
        "multi": [],
        "numeric": {"Dauer (Minuten)": {"min": 1, "max": 240}},
    },
    "Beobachtungsbogen auswerten": {
        "required": ["Bereich", "Rolle", "Auftrag", "Beobachtungsmethode", "Interpretation"],
        "multi": [],
        "numeric": {},
    },
    "Tagesdokumentation erstellen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Situation"],
        "multi": [],
        "numeric": {},
    },
    "Elternbrief verfassen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Anlass"],
        "multi": [],
        "numeric": {},
    },

    # Praxisanleiter:in
    "Anleitung planen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Kompetenzziel", "Aufgabenbeschreibung", "Evaluationskriterium"],
        "multi": ["Kompetenzziel", "Evaluationskriterium"],
        "numeric": {},
    },
    "Feedbackgespräch führen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Kompetenzziel", "Aufgabenbeschreibung", "Evaluationskriterium"],
        "multi": ["Kompetenzziel", "Evaluationskriterium"],
        "numeric": {},
    },

    # Kita-Leitung
    "Teammeeting vorbereiten": {
        "required": ["Bereich", "Rolle", "Auftrag", "Anlass", "Ziel des Gesprächs"],
        "multi": [],
        "numeric": {"Dauer (Minuten)": {"min": 10, "max": 240}},
    },
    "Dienstplanung erstellen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Rahmen", "Planungszeitraum (KW/Monat)", "Schichtmodell", "Mindestbesetzung je Zeitslot"],
        "multi": ["Schichtmodell"],
        "numeric": {},
    },
    "Konzept weiterentwickeln": {
        "required": ["Bereich", "Rolle", "Auftrag", "Thema", "Zielbild / Outcome", "Maßnahmen/Meilensteine"],
        "multi": ["Thema", "Konzeptbaustein(e)"],
        "numeric": {},
    },
    "Qualitätszirkel dokumentieren": {
        "required": ["Bereich", "Rolle", "Auftrag", "Beobachtungsmethode", "Situation", "Evaluationskriterium", "Maßnahmen/Follow-up"],
        "multi": ["Evaluationskriterium"],
        "numeric": {},
    },
    "Jahresplanung erstellen": {
        "required": ["Bereich", "Rolle", "Auftrag", "Rahmen", "Planungszeitraum (Jahr/KW)"],
        "multi": [],
        "numeric": {},
    },
    "Krisenkommunikation vorbereiten": {
        "required": ["Bereich", "Rolle", "Auftrag", "Anlass", "Ziel des Gesprächs", "Kontaktkette/Verantwortlichkeiten"],
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

# ---------- ROUTES ----------
@app.get("/")
def index():
    return render_template_string(TEMPLATE,
        tree_json=json.dumps(DOMAIN_TREE, ensure_ascii=False),
        meta_json=json.dumps(DOMAIN_META, ensure_ascii=False),
        template_text=PROMPT_TEMPLATE
    )

@app.post("/compose")
def compose():
    sel = request.json or {}
    data = {k: "" for k in DEFAULT_KEYS}
    for k, v in sel.items():
        data[k] = ", ".join(v) if isinstance(v, list) else v
    prompt = PROMPT_TEMPLATE.format(**data)
    issues = validate(sel)
    return jsonify({"prompt": prompt, "issues": issues})

# ---------- SERVER-SIDE VALIDATION ----------
def validate(selections: dict) -> list[str]:
    issues: list[str] = []
    for core in ["Bereich", "Rolle", "Auftrag"]:
        if not selections.get(core):
            issues.append(f"Pflichtfeld fehlt: {core}")
    meta = DOMAIN_META.get(selections.get("Auftrag") or "", {})
    for key in meta.get("required", []):
        val = selections.get(key)
        if isinstance(val, list):
            if not val:
                issues.append(f"Pflichtfeld (Mehrfachauswahl) fehlt: {key}")
        else:
            if val in (None, ""):
                issues.append(f"Pflichtfeld fehlt: {key}")
    for key, rng in meta.get("numeric", {}).items():
        raw = selections.get(key)
        if raw in (None, ""):
            continue
        try:
            num = float(str(raw).replace(",", "."))
        except Exception:
            issues.append(f"{key}: muss eine Zahl sein")
            continue
        if "min" in rng and num < rng["min"]:
            issues.append(f"{key}: muss ≥ {rng['min']} sein")
        if "max" in rng and num > rng["max"]:
            issues.append(f"{key}: muss ≤ {rng['max']} sein")
    return issues

# ---------- TEMPLATE (HTML + JS) ----------
TEMPLATE = r"""
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Prompt-Builder — Elementarpädagogik</title>
  <style>
    :root { --c1:#2563eb; --warn:#ef4444; --muted:#6b7280; --ok:#16a34a; }
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin:0; color:#0f172a; }
    header{ padding:10px 16px 0; }
    .banner{
      border:2px solid var(--warn); background:#fee2e2; color:#991b1b;
      padding:12px 16px; border-radius:8px; font-weight:700; margin:12px 16px;
    }
    .container{ display:grid; grid-template-columns: 1.2fr 1fr; gap:24px; padding:12px 16px 32px; }
    h1{ font-size:22px; margin:8px 16px; }
    h2{ font-size:18px; margin:14px 0; }
    .card{ border:1px solid #e5e7eb; border-radius:12px; padding:14px; }
    label{ display:block; font-weight:600; margin:10px 0 6px; }
    select, input[type="text"], textarea {
      width:100%; padding:10px; border:1px solid #e5e7eb; border-radius:8px; font-size:14px;
    }
    textarea { min-height:90px; }
    .row{ display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .muted{ color:var(--muted); font-size:12px; }
    .danger{ color:#b91c1c; }
    .btn{ background:var(--c1); color:#fff; padding:10px 12px; border:none; border-radius:8px; cursor:pointer; font-weight:600; }
    .btn.outline{ background:#fff; color:var(--c1); border:1px solid var(--c1); }
    .issue{ background:#fef3c7; border:1px solid #f59e0b; padding:8px; border-radius:8px; margin:6px 0; font-size:14px; }
    pre{ background:#0b1221; color:#e5e7eb; padding:12px; border-radius:8px; overflow:auto; }
    .copy { margin-top:8px; }
    .sticky { position: sticky; top: 12px; }
  </style>
</head>
<body>
  <header>
    <div class="banner">
      ⚠️ Wichtig (Datenschutz): Keine personenbezogenen Daten eingeben und
      nicht so formulieren, dass ein Rückschluss auf ein bestimmtes Kind möglich ist.
    </div>
    <h1>🧭 Geführter Prompt-Builder — Elementarpädagogik</h1>
  </header>

  <div class="container">
    <!-- LEFT -->
    <div>
      <div class="card sticky">
        <h2>Zwischenstand</h2>
        <div id="preview" class="muted">Noch nichts erfasst.</div>
      </div>

      <div class="card" style="margin-top:16px">
        <h2>Schritte</h2>
        <div class="muted">Bereich: <strong>Elementarpädagogik</strong> (fest)</div>

        <label for="rolle">Rolle</label>
        <select id="rolle"><option value=""></option></select>

        <label for="auftrag">Auftrag</label>
        <select id="auftrag"><option value=""></option></select>

        <div id="fields"></div>

        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:12px">
          <button class="btn outline" id="reset">🔄 Zurücksetzen</button>
          <button class="btn outline" id="previewBtn">👁️ Vorschau</button>
          <button class="btn" id="generate">✨ Prompt erzeugen</button>
        </div>
        <div id="issues"></div>
      </div>
    </div>

    <!-- RIGHT -->
    <div>
      <div class="card">
        <h2>Ergebnis</h2>
        <pre id="result" style="min-height:240px"></pre>
        <div class="copy">
          <button class="btn outline" id="copy">📋 In die Zwischenablage kopieren</button>
          <a id="dl-txt" class="btn outline" download="prompt_output.txt">TXT</a>
          <a id="dl-json" class="btn outline" download="prompt.json">JSON</a>
          <a id="dl-md" class="btn outline" download="prompt.md">Markdown</a>
        </div>
      </div>

      <div class="card" style="margin-top:16px">
        <h2>Hinweise</h2>
        <div>- Pflichtfelder werden geprüft, bevor der Prompt erzeugt wird.</div>
        <div>- An sensiblen Feldern <span class="muted">(z. B. „Kind-Profil“, „Situation“)</span> erscheint ein kleiner Datenschutz-Hinweis.</div>
      </div>
    </div>
  </div>

<script>
const TREE = {{ tree_json|safe }};
const META = {{ meta_json|safe }};
const TEMPLATE = {{ template_text|tojson }};

const sensitiveKeys = new Set(["Kind-Profil (Stärken/Bedarfe)", "Situation", "Interpretation"]);

const state = {
  Bereich: "Elementarpädagogik",
  Rolle: "",
  Aufrag: ""
};

function $(id){ return document.getElementById(id); }

function setOptions(selectEl, options){
  selectEl.innerHTML = '<option value=""></option>' + options.map(o => `<option>${o}</option>`).join("");
}

function updatePreview(){
  const lines = [];
  for (const [k,v] of Object.entries(state)){
    if (!v || k==="prompt") continue;
    lines.push(`${k}: ${Array.isArray(v)? v.join(", ") : v}`);
  }
  $("preview").textContent = lines.length? "• " + lines.join("\n• ") : "Noch nichts erfasst.";
}

function buildFields(){
  const container = $("fields");
  container.innerHTML = "";
  $("issues").innerHTML = "";

  if(!state.Rolle || !state.Auftrag) return;

  const leaf = TREE["Bereich"]["Elementarpädagogik"]["Rolle"][state.Rolle]["Auftrag"][state.Auftrag];
  const meta = META[state.Auftrag] || {multi:[], required:[], numeric:{}};

  for (const [key, sub] of Object.entries(leaf)) {
    const wrap = document.createElement("div");
    const lbl = document.createElement("label");
    lbl.textContent = key;
    wrap.appendChild(lbl);

    if (Array.isArray(sub)) {
      if ((meta.multi||[]).includes(key)) {
        const sel = document.createElement("select");
        sel.multiple = true;
        sel.size = Math.min(6, sub.length);
        sel.style.minHeight = "90px";
        sel.innerHTML = sub.map(o => `<option>${o}</option>`).join("");
        sel.onchange = () => { state[key] = Array.from(sel.selectedOptions).map(o=>o.value); updatePreview(); };
        if (Array.isArray(state[key])) {
          for (const opt of sel.options) opt.selected = state[key].includes(opt.value);
        }
        wrap.appendChild(sel);
      } else {
        const sel = document.createElement("select");
        sel.innerHTML = '<option value=""></option>' + sub.map(o => `<option>${o}</option>`).join("");
        sel.value = state[key] || "";
        sel.onchange = () => { state[key] = sel.value; updatePreview(); };
        wrap.appendChild(sel);
      }
    } else if (sub === "freitext") {
      const isLong = /beschreibung|material|besonder|situation|interpretation|förder|profil|ziel|maßnahmen|zeitplan|planungs/i.test(key);
      if (key === "Dauer (Minuten)") {
        const inp = document.createElement("input");
        inp.type = "text";
        inp.value = state[key] || "";
        inp.oninput = () => { state[key] = inp.value; updatePreview(); };
        wrap.appendChild(inp);
        const rng = (meta.numeric||{})["Dauer (Minuten)"];
        const hint = document.createElement("div");
        hint.className = "muted";
        hint.textContent = rng ? `Zahl erwartet (${rng.min}–${rng.max})` : "Zahl erwartet";
        wrap.appendChild(hint);
      } else {
        const el = isLong ? document.createElement("textarea") : document.createElement("input");
        if(!isLong) el.type = "text";
        el.value = state[key] || "";
        el.oninput = () => { state[key] = el.value; updatePreview(); };
        wrap.appendChild(el);
        if (sensitiveKeys.has(key)) {
          const cap = document.createElement("div");
          cap.className = "muted";
          cap.textContent = "Hinweis Datenschutz: bitte neutral/abstrahiert formulieren, keine personenbezogenen Details.";
          wrap.appendChild(cap);
        }
      }
    }
    container.appendChild(wrap);
  }
}

function validateClient(){
  const issues = [];
  if (!state.Bereich) issues.push("Pflichtfeld fehlt: Bereich");
  if (!state.Rolle) issues.push("Pflichtfeld fehlt: Rolle");
  if (!state.Auftrag) issues.push("Pflichtfeld fehlt: Auftrag");

  const meta = META[state.Auftrag] || {};
  for (const key of (meta.required || [])) {
    const v = state[key];
    if (Array.isArray(v)) { if (!v.length) issues.push(`Pflichtfeld (Mehrfachauswahl) fehlt: ${key}`); }
    else { if (!v) issues.push(`Pflichtfeld fehlt: ${key}`); }
  }
  for (const [key, rng] of Object.entries(meta.numeric || {})) {
    const raw = state[key];
    if (!raw) continue;
    const num = parseFloat(String(raw).replace(",", "."));
    if (Number.isNaN(num)) issues.push(`${key}: muss eine Zahl sein`);
    else {
      if (rng.min!=null && num < rng.min) issues.push(`${key}: muss ≥ ${rng.min} sein`);
      if (rng.max!=null && num > rng.max) issues.push(`${key}: muss ≤ ${rng.max} sein`);
    }
  }
  return issues;
}

function showIssues(list){
  const box = $("issues");
  box.innerHTML = "";
  if (!list.length) return;
  const h = document.createElement("div");
  h.innerHTML = "<h3 class='danger'>Bitte korrigieren:</h3>";
  box.appendChild(h);
  for (const m of list) {
    const d = document.createElement("div");
    d.className = "issue";
    d.textContent = "• " + m;
    box.appendChild(d);
  }
}

function $(id){ return document.getElementById(id); }

// init selects
(function init(){
  const rollen = Object.keys(TREE["Bereich"]["Elementarpädagogik"]["Rolle"]);
  setOptions($("rolle"), rollen);

  $("rolle").onchange = () => {
    state.Rolle = $("rolle").value;
    state.Auftrag = "";
    setOptions($("auftrag"), state.Rolle ? Object.keys(TREE["Bereich"]["Elementarpädagogik"]["Rolle"][state.Rolle]["Auftrag"]) : []);
    for (const k of Object.keys(state)) if (!["Bereich","Rolle","Auftrag"].includes(k)) delete state[k];
    buildFields(); updatePreview();
  };

  $("auftrag").onchange = () => {
    state.Auftrag = $("auftrag").value;
    for (const k of Object.keys(state)) if (!["Bereich","Rolle","Auftrag"].includes(k)) delete state[k];
    buildFields(); updatePreview();
  };

  $("reset").onclick = () => {
    for (const k of Object.keys(state)) delete state[k];
    state.Bereich = "Elementarpädagogik";
    $("rolle").value = ""; $("auftrag").value = "";
    $("fields").innerHTML = ""; $("issues").innerHTML = ""; $("result").textContent="";
    updatePreview();
  };

  $("previewBtn").onclick = async () => {
    const issues = validateClient();
    showIssues(issues);
    if (issues.length) { return; }
    const res = await fetch("/compose", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(state)});
    const data = await res.json();
    $("result").textContent = data.prompt || "";
    updateDownloads(data.prompt);
  };

  $("generate").onclick = $("previewBtn").onclick;

  $("copy").onclick = () => {
    const txt = $("result").textContent || "";
    const ta = document.createElement("textarea");
    ta.value = txt; document.body.appendChild(ta); ta.select();
    document.execCommand("copy"); document.body.removeChild(ta);
    $("copy").textContent = "✅ Kopiert";
    setTimeout(()=>{$("copy").textContent="📋 In die Zwischenablage kopieren"}, 1000);
  };

  updatePreview();
})();

function updateDownloads(text){
  const blobTxt = new Blob([text], {type:"text/plain"});
  $("dl-txt").href = URL.createObjectURL(blobTxt);

  const blobJson = new Blob([JSON.stringify(state, null, 2)], {type:"application/json"});
  $("dl-json").href = URL.createObjectURL(blobJson);

  const md = "## Prompt\\n\\n````\\n" + text + "\\n````\\n";
  const blobMd = new Blob([md], {type:"text/markdown"});
  $("dl-md").href = URL.createObjectURL(blobMd);
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
