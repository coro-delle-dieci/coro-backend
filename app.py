from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # serve per evitare errori CORS in locale

@app.route('/crea-canto', methods=['POST'])
def crea_canto():
    title = request.form.get('title')
    lyrics = request.form.get('lyrics')
    youtube = request.form.get('youtubeLink')
    minicorale = request.form.get('minicoraleNumber')
    assemblea = request.form.get('assembleaNumber')

    if not title or not lyrics:
        return jsonify({'error': 'Titolo e testo obbligatori'}), 400

    if not os.path.exists("canti"):
        os.makedirs("canti")

    filename = f"canti/{title.replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Titolo: {title}\n\n{lyrics}\n")
        if youtube:
            f.write(f"\nYouTube: {youtube}")
        if minicorale:
            f.write(f"\nNumero Minicorale: {minicorale}")
        if assemblea:
            f.write(f"\nNumero Assemblea: {assemblea}")

    return jsonify({'message': 'Canto salvato!'})

if __name__ == '__main__':
    app.run(debug=True)