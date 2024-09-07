import os
import shutil
import pytest
from flask import url_for
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    # Cria o diretório de uploads para testes se ele não existir
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.test_client() as client:
        yield client

    # Limpa os arquivos no diretório de uploads de testes após os testes
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))

def test_index_get(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<h1>Vizuall</h1>' in response.data

def test_index_post_without_image(client):
    response = client.post('/', data={})
    assert response.status_code == 200
    assert b'Nenhuma imagem carregada' in response.data

def test_index_post_with_image(client):
    source_image_path = 'teste.jpeg'
    destination_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'teste.jpeg')

    # Copia a imagem existente para o diretório de uploads
    shutil.copy(source_image_path, destination_image_path)

    # Envia a imagem para a rota de teste
    with open(destination_image_path, 'rb') as img:
        data = {'imagem': (img, 'teste.jpeg')}
        response = client.post('/', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        assert b'Acesso liberado' in response.data or b'Acesso restrito' in response.data

    # Remove a imagem do diretório de uploads após o teste
    os.remove(destination_image_path)
    
def test_index_post_with_restricted_image(client):
    # Cria a imagem de teste de acesso restrito
    restricted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'restricted.jpeg')
    create_restricted_image(restricted_image_path)
    
    # Envia a imagem para a rota de teste
    with open(restricted_image_path, 'rb') as img:
        data = {'imagem': (img, 'restricted.jpeg')}
        response = client.post('/', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        assert b'Acesso restrito' in response.data

def create_restricted_image(filename):
    from PIL import Image, ImageDraw

    # Cria uma nova imagem RGB de 100x100 pixels
    img = Image.new('RGB', (100, 100), color=(0, 255, 0))  # Verde para visibilidade

    d = ImageDraw.Draw(img)
    d.text((10, 40), "Sem acesso", fill=(255, 0, 0))  # Texto vermelho

    # Salva a imagem
    img.save(filename)
