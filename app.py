from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configurazione CORS specifica per GitHub Pages
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://coro-delle-dieci.github.io"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Percorsi file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'canti')
DATA_FILE = os.path.join(BASE_DIR, 'data', 'canti.json')

# Crea cartelle se non esistono
os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Dati iniziali
DEFAULT_DATA = {
    "domenica": datetime.now().strftime("%d %B %Y"),
    "canti": []
}

# Helper functions
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT_DATA.copy()

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

# Endpoints
@app.route('/api/canti', methods=['GET'])
def get_songs():
    return jsonify(load_data())

@app.route('/api/canti', methods=['POST'])
def update_songs():
    try:
        data = request.get_json()
        if not data or 'domenica' not in data or 'canti' not in data:
            return jsonify({"error": "Dati mancanti"}), 400
        
        new_data = {
            "domenica": data['domenica'],
            "canti": [c for c in data['canti'] if isinstance(c, str) and c.strip()]
        }
        
        if save_data(new_data):
            return jsonify({"message": "Dati salvati"})
        return jsonify({"error": "Errore salvataggio"}), 500
    except Exception:
        return jsonify({"error": "Errore server"}), 500

@app.route('/api/songs-list', methods=['GET'])
def list_songs():
    try:
        songs = []
        for f in os.listdir(SONGS_DIR):
            if f.endswith('.html'):
                name = f[:-5].replace('-', ' ').title()
                songs.append(name)
        return jsonify(sorted(songs))
    except Exception:
        return jsonify({"error": "Errore lettura canti"}), 500

@app.route('/')
def home():
    return "Backend Coro delle Dieci"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))