from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# Configurazione
app = Flask(__name__)

# CORS Config - Specifica gli origin permessi
cors = CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://coro-delle-dieci.github.io",
            "http://localhost:*"  # Per sviluppo locale
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

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
    """Carica i dati dei canti dal file JSON"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading songs data: {e}")
    
    return {
        "domenica": datetime.now().strftime("%d %B %Y"),
        "canti": []
    }

def save_songs_data(data):
    """Salva i dati dei canti nel file JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving songs data: {e}")
        return False

# Routes
@app.route('/api/canti', methods=['GET'])
def get_current_songs():
    """Endpoint per ottenere i canti correnti"""
    return jsonify(load_songs_data())

@app.route('/api/canti', methods=['POST'])
def update_songs():
    """Endpoint per aggiornare i canti"""
    try:
        data = request.get_json()
        
        if not data or 'domenica' not in data or 'canti' not in data:
            return jsonify({"error": "Dati mancanti o non validi"}), 400
        
        # Validazione e pulizia dei dati
        valid_songs = [
            str(song).strip() 
            for song in data['canti'] 
            if str(song).strip()
        ]
        
        new_data = {
            "domenica": str(data['domenica']).strip(),
            "canti": valid_songs
        }
        
        if save_songs_data(new_data):
            logger.info(f"Canti aggiornati per {new_data['domenica']}")
            return jsonify({"message": "Aggiornato con successo"})
        
        return jsonify({"error": "Errore nel salvataggio"}), 500
        
    except Exception as e:
        logger.error(f"Errore in update_songs: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

@app.route('/api/songs-list', methods=['GET'])
def list_available_songs():
    """Endpoint per la lista dei canti disponibili"""
    try:
        if not os.path.exists(SONGS_DIR):
            logger.error(f"Cartella canti non trovata: {SONGS_DIR}")
            return jsonify({"error": "Cartella canti non configurata"}), 500
            
        songs = []
        for filename in os.listdir(SONGS_DIR):
            if filename.endswith('.html'):
                try:
                    # Estrae il titolo dal filename (es: "canto-natale.html" -> "Canto Natale")
                    song_name = (
                        os.path.splitext(filename)[0]
                        .replace('-', ' ')
                        .title()
                    )
                    songs.append(song_name)
                except Exception as e:
                    logger.warning(f"Errore elaborazione file {filename}: {e}")
        
        if not songs:
            logger.warning("Nessun canto trovato nella cartella")
            return jsonify({"error": "Nessun canto disponibile"}), 404
            
        return jsonify(sorted(songs))
        
    except Exception as e:
        logger.error(f"Errore in list_available_songs: {str(e)}")
        return jsonify({"error": "Errore nel recupero della lista"}), 500

@app.route('/canti/<filename>')
def serve_song(filename):
    """Serve i file dei canti"""
    try:
        return send_from_directory(SONGS_DIR, filename)
    except FileNotFoundError:
        logger.warning(f"File non trovato: {filename}")
        return jsonify({"error": "Canto non trovato"}), 404
    except Exception as e:
        logger.error(f"Errore in serve_song: {str(e)}")
        return jsonify({"error": "Errore interno"}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "coro-backend",
        "timestamp": datetime.now().isoformat(),
        "songs_dir": SONGS_DIR,
        "data_file": DATA_FILE
    })

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico', 
        mimetype='image/vnd.microsoft.icon'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))