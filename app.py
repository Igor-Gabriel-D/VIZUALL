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
        with open('db/logs.json', 'r') as file:
            logs = json.load(file)
    except FileNotFoundError:
        logs = []  # Se o arquivo não existir, inicia uma lista vazia

    # Adiciona o novo log
    logs.append(log_entry)

    # Salva o log atualizado de volta no arquivo
    with open('db/logs.json', 'w') as file:
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
                    usuario = dfs[0]['identity'].iloc[0][11:35]  # Obtém o primeiro usuário identificado
                    print(usuario)
                    
                    publish_message("bloco/1/sala/1/acesso", "liberado")

                    # Registra o log de acesso com usuário identificado, bloco e sala
                    registrar_log( usuario, "66c71de92bcf9624eb462599", "1")

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

@app.route('/sala', methods=['GET'])
def get_sala():
    # Obtém os parâmetros de bloco e sala da URL
    bloco_param = request.args.get('bloco')
    sala_param = request.args.get('sala')

    if not bloco_param or not sala_param:
        return jsonify({"error": "Parâmetros 'bloco' e 'sala' são necessários"}), 400

    try:
        # Lê o conteúdo dos arquivos de log e usuários
        with open('db/logs.json', 'r') as file:
            logs = json.load(file)
        with open('db/usuarios.json', 'r') as file:
            usuarios = json.load(file)

        # Filtra os logs pelo bloco e sala fornecidos
        logs_filtrados = [
            log for log in logs
            if str(log.get('bloco')) == str(bloco_param) and str(log.get('sala')) == str(sala_param)
        ]

        # Mapeia o ID do usuário para o nome a partir do arquivo de usuários
        usuario_map = {usuario['id']: usuario['nome'] for usuario in usuarios}

        # Constrói a resposta com o nome do usuário e o horário do log
        resultado = []
        for log in logs_filtrados:
            nome_usuario = usuario_map.get(log['usuario'], "Usuário não encontrado")
            resultado.append({
                "nome": nome_usuario,
                "horario": log['horario']
            })

        return jsonify(resultado)

    except FileNotFoundError:
        return jsonify({"error": "Arquivo não encontrado"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Erro ao decodificar o arquivo JSON"}), 500


if __name__ == '__main__':
    app.run(debug=False, port=8000)
