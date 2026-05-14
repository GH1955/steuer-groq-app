from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

SYSTEM_PROMPT = """Du bist eine Steuerapp. Befolge ausschließlich die im Space hinterlegten Anweisungen. Antworte stets so kurz wie möglich und in genau 5 Abschnitten.

1. Antwort: Beantworte die Frage ausschließlich auf Basis der hochgeladenen PDF-Dateien. Verwende keine Verweise auf Stichwortverzeichnisse. Führe bei jeder Aussage zwingend das Arbeitsbuch mit Titel, Jahr und den konkreten Seitenzahlen aller verwendeten Fundstellen an.

2. Antwort: Durchsuche ausschließlich die Findok unter https://findok.bmf.gv.at/findok/ und gib in wenigen kurzen Absätzen an, was du dort findest. Nenne die genauen Quellen in der Findok und die jeweiligen Randzahlen (Rz). Verwende keine anderen Quellenangaben außerhalb der Findok.

3. Antwort: Durchsuche das Web nach weiteren Informationen zur gestellten Frage und ergänze die bisherigen Antworten nur insoweit, als du weitere nützliche Informationen findest. Nenne hier keine Quellenangaben betreffend die Arbeitsbücher und keine Quellenangaben betreffend die Findok.

4. Fachliteratur: Finde Fachliteratur zur gestellten Frage bei LexisNexis oder Linde.

5. Zusammenfassung: Fasse die Antworten 1 bis 4 unter der Überschrift '5. Zusammenfassung:' zusammen. Frage danach, ob weitere Fragen bestehen und ob die Antwort verbessert oder präzisiert werden soll.

Stilregeln: Alle Überschriften sind fett. Jede Antwort kann aus mehreren kurzen Absätzen bestehen. Zwischen Absätzen steht eine Leerzeile. Nimm Beispiele auf. Wenn Beträge oder Zahlen vorkommen, die sich tabellarisch darstellen lassen, verwende eine übersichtliche Tabelle."""


def groq_client():
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise RuntimeError('GROQ_API_KEY ist nicht gesetzt')
    return Groq(api_key=api_key)


def search_findok(query: str) -> str:
    """Durchsucht die Findok (BMF) nach steuerrechtlichen Informationen."""
    try:
        search_url = "https://findok.bmf.gv.at/findok/findok_suche.do"
        params = {"suchwort": query, "action": "suche"}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Findok nicht erreichbar (Status {response.status_code})."
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select(".ergebnis, .treffer, li.result, .searchResult")[:5]:
            text = item.get_text(separator=" ", strip=True)
            if text:
                results.append(text)
        if not results:
            for p in soup.find_all("p")[:8]:
                text = p.get_text(strip=True)
                if len(text) > 40:
                    results.append(text)
        return "\n\n".join(results) if results else "Keine Treffer in der Findok gefunden."
    except Exception as e:
        return f"Fehler bei der Findok-Suche: {str(e)}"


def search_general_web(query: str) -> str:
    """Durchsucht das Web über DuckDuckGo nach steuerrelevanten Informationen."""
    try:
        search_url = "https://html.duckduckgo.com/html/"
        params = {"q": query + " Österreich Steuer"}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.post(search_url, data=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Websuche nicht erreichbar (Status {response.status_code})."
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.select(".result__body, .result__snippet")[:5]:
            text = result.get_text(separator=" ", strip=True)
            if text and len(text) > 30:
                results.append(text)
        return "\n\n".join(results) if results else "Keine Web-Ergebnisse gefunden."
    except Exception as e:
        return f"Fehler bei der Websuche: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/api/chat')
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    history = data.get('history') or []
    if not question:
        return jsonify({'error': 'Bitte eine Frage eingeben.'}), 400
    try:
        client = groq_client()
        findok_results = search_findok(question)
        web_results = search_general_web(question)
        context = f"--- Findok-Suchergebnisse ---\n{findok_results}\n\n--- Web-Suchergebnisse ---\n{web_results}"
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        for item in history[-8:]:
            role = item.get('role')
            content = item.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})
        messages.append({'role': 'user', 'content': f"{question}\n\nHier sind aktuelle Suchergebnisse zur Unterstützung:\n{context}"})
        completion = client.chat.completions.create(
            model=os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=messages,
            temperature=0.2,
            max_completion_tokens=2000,
        )
        answer = completion.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
