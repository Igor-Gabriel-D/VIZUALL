from flask import Flask, render_template, request, url_for, jsonify
import paho.mqtt.client as mqtt
from deepface import DeepFace
# from time import sleep
import os
import requests
import subprocess
import json
from datetime import datetime  # Para registrar a hora atual


# Função para registrar o log
def registrar_log(usuario, bloco, sala):
    log_entry = {
        "horario": datetime.now().strftime("%Y%m%d%H%M%S"),  # Timestamp formatado
        "usuario": usuario,
        "bloco": bloco,
        "sala": sala
    }

    # Verifica se o arquivo de log existe e lê o conteúdo existente
    try:
        with open('log_acessos.json', 'r') as file:
            logs = json.load(file)
    except FileNotFoundError:
        logs = []  # Se o arquivo não existir, inicia uma lista vazia

    # Adiciona o novo log
    logs.append(log_entry)

    # Salva o log atualizado de volta no arquivo
    with open('log_acessos.json', 'w') as file:
        json.dump(logs, file, indent=4)




# Função para enviar mensagens MQTT
def publish_message(topic, message):
    command = ['mosquitto_pub', '-h', '20.68.52.33', '-t', topic, '-m', message]
    subprocess.run(command, check=True)


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        imagem_path = None

        if 'imagem' in request.files:
            imagem = request.files['imagem']

            if imagem.filename != '':
                imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem.filename))
                print(f'Imagem salva: {imagem.filename}')
                imagem_path = url_for('static', filename=f'uploads/{imagem.filename}')

        if imagem_path:
            try:
                dfs = DeepFace.find(
                    img_path=f"static/uploads/{imagem.filename}",
                    db_path="./usuarios"
                )

                if dfs[0]['identity'].notnull().any():
                    usuario = dfs[0]['identity'].iloc[0]  # Obtém o primeiro usuário identificado
                    print(usuario)
                    
                    publish_message("bloco/1/sala/1/acesso", "liberado")

                    # Registra o log de acesso com usuário identificado, bloco e sala
                    registrar_log(usuario=usuario, bloco="66c71de92bcf9624eb462599", sala="1")

                    return jsonify({
                        "mensagem": "Acesso liberado",
                        "imagem_path": imagem_path
                    })
                else:
                    return jsonify({
                        "mensagem": "Acesso restrito",
                        "imagem_path": imagem_path
                    })
            except Exception as e:
                print(f"Erro: {e}")
                return jsonify({
                    "mensagem": "Acesso restrito: Não foi possível detectar um rosto na imagem.",
                    "imagem_path": None
                })
        else:
            return jsonify({
                "mensagem": "Nenhuma imagem carregada",
                "imagem_path": None
            })
    return render_template('index.html')

@app.route('/salas', methods=['GET'])
def get_blocos():
    try:
        with open('db/salas.json', 'r') as file:
            blocos_data = json.load(file)  # Lê o conteúdo do arquivo JSON
        return jsonify(blocos_data)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo blocos.json não encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=False, port=8000)
