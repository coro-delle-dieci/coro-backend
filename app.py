from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # per evitare problemi CORS

# Carica i canti da un file JSON o variabile
canti_data = {
    "domenica": "23 giugno 2025",
    "canti": ["Canto 1", "Canto 2", "Canto 3"]
}

@app.route('/api/canti', methods=['GET'])
def get_canti():
    return jsonify(canti_data)

@app.route('/api/canti', methods=['POST'])
def update_canti():
    global canti_data
    # verifica autenticazione Basic (semplificata)
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'password':
        return jsonify({"error": "Unauthorized"}), 401

    dati = request.json
    canti_data = dati  # o valida i dati prima di salvare
    return jsonify({"message": "Canti aggiornati"}), 200

if __name__ == "__main__":
    app.run()