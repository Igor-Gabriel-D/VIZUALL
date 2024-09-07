# from flask import Flask, render_template, request
from flask import Flask, render_template, request, url_for
import paho.mqtt.client as mqtt
from deepface import DeepFace

# from flask_cors import CORS
import os

# Define as funções de callback
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker com código: " + str(rc))

def on_message(client, userdata, message):
    print("Mensagem recebida: " + str(message.payload.decode("utf-8")))

# Cria um cliente MQTT
client = mqtt.Client()

# Define as funções de callback
client.on_connect = on_connect
client.on_message = on_message

# Conecta-se ao broker
client.connect("broker.hivemq.com", 1883, 60)


app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        imagem_path = None

        if 'imagem' in request.files:
            imagem = request.files['imagem']

            # Salva a imagem no diretório definido
            if imagem.filename != '':
                imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem.filename))
                print(f'Imagem salva: {imagem.filename}')
                imagem_path = url_for('static', filename=f'uploads/{imagem.filename}')

        if imagem_path:
            try:
                dfs = DeepFace.find(
                    img_path=f"static/uploads/{imagem.filename}",
                    db_path="./usuarios",
                    enforce_detection=True  # Você pode alterar isso para False se desejar
                )

                if dfs[0]['identity'].notnull().any():
                    print(dfs[0]['identity'])
                    client.publish("bloco/1/sala/1/acesso", "liberado")

                    return f"""
                        <h1>Acesso liberado</h1>
                        <img src="{imagem_path}" alt="Imagem carregada">
                    """
                else:
                    return "<h1>Acesso restrito</h1>"
            except ValueError as e:
                # Se a detecção de rosto falhar, retorna uma mensagem apropriada
                print(f"Erro: {e}")
                return "<h1>Acesso restrito</h1><p>Não foi possível detectar um rosto na imagem.</p>"
        else:
            return """
                <h1>Informações Recebidas</h1>
                <p>Nenhuma imagem carregada.</p>
            """
    return """<!DOCTYPE html>
              <html lang="pt-br">
              <head>
                  <meta charset="UTF-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <title>Formulário</title>
              </head>
              <body>
                  <h1>Vizuall</h1>

                  <form method="POST" action="" enctype="multipart/form-data">
                      <label for="imagem">Escolha uma imagem:</label>
                      <input type="file" id="imagem" name="imagem"><br><br>
                      <input type="submit" value="Enviar">
                  </form>
              </body>
              </html>
          """
if __name__ == '__main__':
    app.run(debug=False, port=8000)