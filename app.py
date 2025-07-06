from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le rotte (limitare in produzione)

# Configurazione
app.config.update({
    'SONGS_DIR': os.path.join(os.path.dirname(__file__), 'canti'),
    'DATA_FILE': os.path.join(os.path.dirname(__file__), 'data', 'canti.json')
})

# Crea le cartelle necessarie se non esistono
os.makedirs(app.config['SONGS_DIR'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['DATA_FILE']), exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_canti_data():
    """Carica i dati dei canti dal file JSON"""
    try:
        if os.path.exists(app.config['DATA_FILE']):
            with open(app.config['DATA_FILE'], 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading canti data: {str(e)}")
    
    # Dati di default se il file non esiste
    return {
        "domenica": datetime.now().strftime("%d %B %Y"),
        "canti": []
    }

def save_canti_data(data):
    """Salva i dati dei canti nel file JSON"""
    try:
        with open(app.config['DATA_FILE'], 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving canti data: {str(e)}")
        return False

@app.route('/api/canti', methods=['GET'])
def get_canti():
    """Endpoint per ottenere i canti della domenica"""
    return jsonify(load_canti_data())

@app.route('/api/canti', methods=['POST'])
def update_canti():
    """
    Endpoint per aggiornare i canti.
    L'autenticazione è gestita lato client via Basic Auth in credentials.js
    """
    data = request.get_json()
    
    # Validazione minima
    if not data or 'domenica' not in data or 'canti' not in data:
        return jsonify({"error": "Dati mancanti o non validi"}), 400
    
    # Filtra canti vuoti
    valid_canti = [c for c in data['canti'] if isinstance(c, str) and c.strip()]
    
    new_data = {
        "domenica": data['domenica'],
        "canti": valid_canti
    }
    
    if save_canti_data(new_data):
        logger.info(f"Canti aggiornati per {new_data['domenica']}")
        return jsonify({"message": "Canti aggiornati con successo"})
    else:
        return jsonify({"error": "Errore nel salvataggio"}), 500

@app.route('/api/songs-list', methods=['GET'])
def get_songs_list():
    """Endpoint per ottenere la lista dei canti disponibili"""
    try:
        songs = []
        for f in os.listdir(app.config['SONGS_DIR']):
            if f.endswith('.html'):
                # Rimuovi estensione e sostituisci trattini con spazi
                song_name = f[:-5].replace('-', ' ')
                songs.append(song_name)
        return jsonify(sorted(songs))
    except Exception as e:
        logger.error(f"Errore accesso cartella canti: {str(e)}")
        return jsonify({"error": "Errore nel recupero della lista"}), 500

@app.route('/canti/<path:filename>')
def serve_song(filename):
    """Serve i file dei canti dalla cartella /canti"""
    return send_from_directory(app.config['SONGS_DIR'], filename)

@app.route('/health')
def health_check():
    """Endpoint per health check"""
    return jsonify({
        "status": "healthy",
        "service": "coro-backend",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))