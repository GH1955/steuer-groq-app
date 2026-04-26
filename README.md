# Steuer-Assistenz Österreich – Flask + Groq + Railway

Diese App ist eine **eigene Chat-Oberfläche** für Fragen zu Steuern in Österreich. Sie verwendet Flask im Backend, Groq als Modellanbieter und ist für Railway vorbereitet.

## Warum diese Variante

Groq bietet eine Chat/API-Dokumentation und OpenAI-kompatible Nutzung, was sich gut für eigene Apps eignet. Railway bietet eine offizielle Flask-Deploy-Anleitung und eignet sich als einfacher Hoster für so eine App. [web:113][web:120][web:116]

## Inhalt

- `app.py` – Flask-Server mit Chat-Endpunkt
- `templates/index.html` – eigene Oberfläche
- `static/style.css` – Design
- `static/app.js` – Chat-Logik
- `requirements.txt` – Python-Abhängigkeiten
- `Procfile`, `runtime.txt`, `railway.json` – Deployment auf Railway

## Lokal starten

1. Python 3.12 installieren.
2. Im Projektordner ausführen:
   - `python -m venv .venv`
   - macOS/Linux: `source .venv/bin/activate`
   - Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
   - `pip install -r requirements.txt`
3. Groq-API-Key setzen:
   - macOS/Linux: `export GROQ_API_KEY=dein_key`
   - Windows PowerShell: `$env:GROQ_API_KEY="dein_key"`
4. Starten:
   - `python app.py`
5. Öffnen:
   - `http://127.0.0.1:5000`

## Railway deployen

1. Projekt nach GitHub pushen.
2. In Railway: **New Project → Deploy from GitHub Repo**.
3. Repository auswählen.
4. Unter Variablen setzen:
   - `GROQ_API_KEY=dein_key`
   - optional `GROQ_MODEL=llama-3.3-70b-versatile`
5. Deploy starten.

## Hinweis

Die App nutzt einen allgemeinen Österreich-Steuer-Prompt. Wenn du willst, kann sie im nächsten Schritt noch enger auf deine bisherigen Space-Anweisungen oder auf bestimmte Dokumente zugeschnitten werden.
