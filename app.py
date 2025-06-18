from flask import Flask, request, jsonify, abort
import json

app = Flask(__name__)

DATA_FILE = 'canti.json'
USERNAME = 'admin'    # Username finto
PASSWORD = 'password' # Password finta (per test locale)

# Funzione per leggere i canti
def read_canti():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Funzione per scrivere i canti
def write_canti(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Rotta pubblica: restituisce i canti
@app.route('/api/canti', methods=['GET'])
def get_canti():
    return jsonify(read_canti())

# Rotta privata: modifica i canti (richiede autenticazione base)
@app.route('/api/canti', methods=['POST'])
def update_canti():
    auth = request.authorization
    if not auth or auth.username != USERNAME or auth.password != PASSWORD:
        abort(401)  # Unauthorized

    new_canti = request.json
    write_canti(new_canti)
    return jsonify({"message": "Canti aggiornati con successo!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)