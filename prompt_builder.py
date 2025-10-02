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

