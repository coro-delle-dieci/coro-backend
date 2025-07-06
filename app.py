from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# Configurazione
app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'canti')
DATA_FILE = os.path.join(BASE_DIR, 'data', 'canti.json')

# Crea cartelle se non esistono
os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions
def load_songs_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading songs data: {e}")
    
    return {
        "domenica": datetime.now().strftime("%d %B %Y"),
        "canti": []
    }

def save_songs_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving songs data: {e}")
        return False

# Routes
@app.route('/api/canti', methods=['GET'])
def get_current_songs():
    return jsonify(load_songs_data())

@app.route('/api/canti', methods=['POST'])
def update_songs():
    data = request.get_json()
    
    if not data or 'domenica' not in data or 'canti' not in data:
        return jsonify({"error": "Dati mancanti"}), 400
    
    valid_songs = [s for s in data['canti'] if isinstance(s, str) and s.strip()]
    
    if save_songs_data({
        "domenica": data['domenica'],
        "canti": valid_songs
    }):
        return jsonify({"message": "Aggiornato con successo"})
    
    return jsonify({"error": "Errore salvataggio"}), 500

@app.route('/api/songs-list', methods=['GET'])
def list_available_songs():
    try:
        songs = [
            f.replace('.html', '').replace('-', ' ')
            for f in os.listdir(SONGS_DIR)
            if f.endswith('.html')
        ]
        return jsonify(sorted(songs))
    except Exception as e:
        logger.error(f"Error listing songs: {e}")
        return jsonify({"error": "Errore server"}), 500

@app.route('/canti/<filename>')
def serve_song(filename):
    return send_from_directory(SONGS_DIR, filename)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "service": "coro-backend",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))