from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from functools import wraps
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Configurazione dell'applicazione
app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le rotte

# Configurazione del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione sicurezza (in produzione usa variabili d'ambiente)
app.config.update({
    'SECRET_KEY': 'your-secret-key-here',  # Sostituisci con una chiave sicura
    'SONGS_DIR': os.path.join(os.path.dirname(__file__), 'canti'),
    'ADMIN_CREDENTIALS': {
        'admin1': generate_password_hash('password1'),
        'admin2': generate_password_hash('password2'),
        'admin3': generate_password_hash('password3')
    }
})

# Dati iniziali (verranno sovrascritti dalle chiamate POST)
canti_data = {
    "domenica": "23 giugno 2025",
    "canti": ["Canto 1", "Canto 2", "Canto 3"]
}

# Decoratore per l'autenticazione
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            logger.warning("Tentativo di accesso non autenticato")
            return jsonify({"error": "Autenticazione richiesta"}), 401
        
        if auth.username not in app.config['ADMIN_CREDENTIALS']:
            logger.warning(f"Username non riconosciuto: {auth.username}")
            return jsonify({"error": "Credenziali non valide"}), 403
            
        if not check_password_hash(app.config['ADMIN_CREDENTIALS'][auth.username], auth.password):
            logger.warning(f"Password errata per l'utente: {auth.username}")
            return jsonify({"error": "Credenziali non valide"}), 403
            
        return f(*args, **kwargs)
    return decorated

# Rotta principale per ottenere i canti correnti
@app.route('/api/canti', methods=['GET'])
def get_canti():
    try:
        return jsonify(canti_data)
    except Exception as e:
        logger.error(f"Errore in get_canti: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

# Rotta per aggiornare i canti
@app.route('/api/canti', methods=['POST'])
@auth_required
def update_canti():
    global canti_data
    try:
        data = request.get_json()
        
        # Validazione dei dati
        if not data or 'domenica' not in data or 'canti' not in data:
            return jsonify({"error": "Dati mancanti o non validi"}), 400
            
        if not isinstance(data['canti'], list):
            return jsonify({"error": "Il campo 'canti' deve essere una lista"}), 400
            
        # Salva i nuovi dati
        canti_data = {
            "domenica": data['domenica'],
            "canti": [canto for canto in data['canti'] if canto.strip()]
        }
        
        logger.info(f"Canti aggiornati per la domenica: {canti_data['domenica']}")
        return jsonify({"message": "Canti aggiornati con successo"}), 200
        
    except Exception as e:
        logger.error(f"Errore in update_canti: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

# Rotta per ottenere la lista dei canti disponibili
@app.route('/api/songs-list', methods=['GET'])
def get_songs_list():
    try:
        if not os.path.exists(app.config['SONGS_DIR']):
            logger.error(f"Cartella canti non trovata: {app.config['SONGS_DIR']}")
            return jsonify({"error": "Cartella canti non configurata correttamente"}), 500
            
        songs = []
        for f in os.listdir(app.config['SONGS_DIR']):
            if f.endswith('.html') and os.path.isfile(os.path.join(app.config['SONGS_DIR'], f)):
                # Rimuovi l'estensione e decodifica caratteri speciali
                song_name = f[:-5].replace('-', ' ')
                songs.append(song_name)
        
        return jsonify(sorted(songs))
    except Exception as e:
        logger.error(f"Errore in get_songs_list: {str(e)}")
        return jsonify({"error": "Errore nel recupero della lista dei canti"}), 500

# Rotta per servire i file dei canti
@app.route('/canti/<path:filename>')
def serve_song(filename):
    try:
        return send_from_directory(app.config['SONGS_DIR'], filename)
    except FileNotFoundError:
        logger.warning(f"File non trovato: {filename}")
        return jsonify({"error": "Canto non trovato"}), 404
    except Exception as e:
        logger.error(f"Errore in serve_song: {str(e)}")
        return jsonify({"error": "Errore interno del server"}), 500

# Rotta per la verifica dello stato del server
@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok", "service": "coro-backend"})

# Gestione degli errori
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint non trovato"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Errore interno del server"}), 500

if __name__ == '__main__':
    # Verifica che la cartella canti esista
    if not os.path.exists(app.config['SONGS_DIR']):
        os.makedirs(app.config['SONGS_DIR'])
        logger.info(f"Creata cartella canti: {app.config['SONGS_DIR']}")
    
    app.run(host='0.0.0.0', port=5000)