import os
import base64
import requests

def aggiorna_file_su_github(percorso_file, contenuto):
    GH_TOKEN = os.environ['GH_TOKEN']
    GH_OWNER = os.environ['GH_OWNER']
    GH_REPO = os.environ['GH_REPO']

    url_api = f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{percorso_file}"

    # Prima leggo il file per ottenere l'SHA
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    r = requests.get(url_api, headers=headers)
    
    if r.status_code == 200:
        sha = r.json()['sha']
    else:
        sha = None  # File nuovo

    contenuto_base64 = base64.b64encode(contenuto.encode("utf-8")).decode("utf-8")

    dati = {
        "message": "Aggiorno i canti della domenica",
        "content": contenuto_base64,
        "branch": "main"
    }

    if sha:
        dati["sha"] = sha

    response = requests.put(url_api, headers=headers, json=dati)

    if response.status_code in [200, 201]:
        print("✅ File aggiornato con successo")
    else:
        print("❌ Errore:", response.status_code, response.json())