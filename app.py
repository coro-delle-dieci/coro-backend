import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="https://coro-delle-dieci.github.io", supports_credentials=True)


@app.route('/crea-canto', methods=['POST'])
def crea_canto():
    title = request.form.get('title')
    lyrics = request.form.get('lyrics')
    youtube = request.form.get('youtubeLink')
    minicorale = request.form.get('minicoraleNumber')
    assemblea = request.form.get('assembleaNumber')

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

    return jsonify({'message': 'Canto creato con successo!'})