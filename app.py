from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging

# Configurazione Flask
app = Flask(__name__)


@app.route('/crea-canto', methods=['POST'])
def crea_canto():
    title = request.form.get('title')
    lyrics = request.form.get('lyrics')
    youtube = request.form.get('youtubeLink')
    mini = request.form.get('minicoraleNumber')
    assemblea = request.form.get('assembleaNumber')
    
    # Salva i dati (puoi anche salvarli su file o in un database)
    if not os.path.exists("canti"):
        os.makedirs("canti")

    filename = f"canti/{title.replace(' ', '_')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Titolo: {title}\n\nTesto:\n{lyrics}\n")
        if youtube:
            f.write(f"\nYouTube: {youtube}")
        if mini:
            f.write(f"\nNumero Minicorale: {mini}")
        if assemblea:
            f.write(f"\nNumero Assemblea: {assemblea}")
    
    return jsonify({'message': 'Canto creato con successo!'})

if __name__ == '__main__':
    app.run(debug=True)





# Configurazione CORS
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'canti.json')

# Crea cartelle se non esistono
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
@app.route('/api/songs', methods=['GET'])
def get_available_songs():
    """Endpoint per ottenere l'elenco dei canti disponibili"""
    try:
        songs_data = load_songs_data()
        # Simuliamo una lista di canti disponibili
        # In un'app reale, questa potrebbe venire da un database
        available_songs = [
            {"id": "1", "titolo": "Canto di apertura"},
            {"id": "2", "titolo": "Canto di offertorio"},
            {"id": "3", "titolo": "Canto di comunione"},
            {"id": "4", "titolo": "Canto finale"}
        ]
        return jsonify(available_songs)
    except Exception as e:
        logger.error(f"Error in get_available_songs: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

@app.route('/api/current', methods=['GET'])
def get_current_songs():
    """Endpoint per ottenere i canti correnti"""
    try:
        return jsonify(load_songs_data())
    except Exception as e:
        logger.error(f"Error in get_current_songs: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

@app.route('/api/save-songs', methods=['POST'])
def update_songs():
    """Endpoint per aggiornare i canti"""
    try:
        data = request.get_json()
        
        if not data or 'domenica' not in data or 'canti' not in data:
            return jsonify({"error": "Dati mancanti o non validi"}), 400
        
        # Validazione e pulizia dei dati
        valid_songs = []
        for song in data['canti']:
            if isinstance(song, dict):
                if 'id' in song and 'titolo' in song:
                    valid_songs.append({"id": str(song['id']), "titolo": str(song['titolo']).strip()})
                elif 'titolo' in song:
                    valid_songs.append({"titolo": str(song['titolo']).strip(), "link": str(song.get('link', '')).strip()})
        
        new_data = {
            "domenica": str(data['domenica']).strip(),
            "canti": valid_songs
        }
        
        if save_songs_data(new_data):
            logger.info(f"Canti aggiornati per {new_data['domenica']}")
            return jsonify({"message": "Aggiornato con successo"}), 200
        
        return jsonify({"error": "Errore nel salvataggio"}), 500
        
    except Exception as e:
        logger.error(f"Errore in update_songs: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

# Servizio file statici per il frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(os.path.join(BASE_DIR, 'static', path)):
        return send_from_directory(os.path.join(BASE_DIR, 'static'), path)
    else:
        return send_from_directory(os.path.join(BASE_DIR, 'static'), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))