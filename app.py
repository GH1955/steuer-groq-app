from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

SYSTEM_PROMPT = """Du bist eine hilfreiche deutschsprachige Assistenz für Fragen zu Steuern in Österreich.
Antworte klar, sachlich und gut strukturiert auf Deutsch.
Beziehe dich auf Österreich, wenn die Frage nichts anderes sagt.
Wenn Rechts- oder Steuerdetails unklar oder einzelfallabhängig sind, weise knapp darauf hin, dass dies keine individuelle Steuerberatung ersetzt.
Gib praktische Antworten in verständlicher Sprache.
"""


def groq_client():
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise RuntimeError('GROQ_API_KEY ist nicht gesetzt')
    return Groq(api_key=api_key)


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
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        for item in history[-8:]:
            role = item.get('role')
            content = item.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})
        messages.append({'role': 'user', 'content': question})

        completion = client.chat.completions.create(
            model=os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=messages,
            temperature=0.2,
            max_completion_tokens=1200,
        )
        answer = completion.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
