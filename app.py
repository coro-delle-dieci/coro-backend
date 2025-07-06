from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import os
from functools import wraps

app = Flask(__name__)
CORS(app)

# Configurazione sicura (in produzione usa variabili d'ambiente)
app.config['ADMIN_CREDENTIALS'] = {
    'admin1': 'password1',
    'admin2': 'password2',
    'admin3': 'password3'
}

# Dati iniziali
canti_data = {
    "domenica": "23 giugno 2025",
    "canti": ["Canto 1", "Canto 2", "Canto 3"]
}

# Decoratore per verificare l'autenticazione
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username not in app.config['ADMIN_CREDENTIALS'] or \
           app.config['ADMIN_CREDENTIALS'][auth.username] != auth.password:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/canti', methods=['GET'])
def get_canti():
    return jsonify(canti_data)

@app.route('/api/canti', methods=['POST'])
@auth_required
def update_canti():
    global canti_data
    dati = request.json
    
    # Validazione dei dati
    if not dati or 'domenica' not in dati or 'canti' not in dati:
        return jsonify({"error": "Dati mancanti o non validi"}), 400
        
    canti_data = dati
    return jsonify({"message": "Canti aggiornati"}), 200

if __name__ == "__main__":
    app.run()