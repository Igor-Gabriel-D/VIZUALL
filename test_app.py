import os
import shutil
import pytest
from flask import url_for
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.test_client() as client:
        yield client

    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))

def test_index_get(client):
    response = client.get('/')
    assert response.status_code == 200
    assert '<h1>Vizuall Cam</h1>' in response.get_data(as_text=True)

def test_index_post_without_image(client):
    response = client.post('/', data={'bloco': 'A', 'sala': '101'})
    assert response.status_code == 200
    assert 'Nenhuma imagem carregada' in response.get_data(as_text=True)

def test_index_post_with_image(client):
    source_image_path = 'teste.jpeg'
    destination_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'teste.jpeg')

    shutil.copy(source_image_path, destination_image_path)

    with open(destination_image_path, 'rb') as img:
        data = {'imagem': (img, 'teste.jpeg'), 'bloco': 'A', 'sala': '101'}
        response = client.post('/', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        assert 'Acesso liberado' in response.get_data(as_text=True) or 'Acesso restrito' in response.get_data(as_text=True)

    
    os.remove(destination_image_path)
    
def test_index_post_with_restricted_image(client):
    
    restricted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'restricted.jpeg')
    create_restricted_image(restricted_image_path)
    
    with open(restricted_image_path, 'rb') as img:
        data = {'imagem': (img, 'restricted.jpeg'), 'bloco': 'A', 'sala': '101'}
        response = client.post('/', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        assert 'Acesso restrito' in response.get_data(as_text=True)

def test_salas_get(client):
    
    response = client.get('/salas')
    assert response.status_code == 200

    
    salas_data = response.get_json()
    assert salas_data is not None
    assert isinstance(salas_data, list)  

    assert any(bloco['nome_bloco'] == 'Bloco 1' for bloco in salas_data)
    assert any(bloco['nome_bloco'] == 'Bloco 2' for bloco in salas_data)
    assert any(bloco['nome_bloco'] == 'Bloco 3' for bloco in salas_data)

    for bloco in salas_data:
        assert 'nome_bloco' in bloco
        assert 'bloco' in bloco
        assert 'salas' in bloco['bloco']
        assert isinstance(bloco['bloco']['salas'], list)

        for sala in bloco['bloco']['salas']:
            assert 'nome_sala' in sala
            assert 'permissoes' in sala
            assert isinstance(sala['permissoes'], list)

def test_sala_get(client):
    bloco_param = '66c71de92bcf9624eb462599'
    sala_param = '1'

    response = client.get('/sala', query_string={'bloco': bloco_param, 'sala': sala_param})
    
    assert response.status_code == 200
    
    sala_data = response.get_json()
    assert sala_data is not None
    
    for item in sala_data:
        assert 'nome' in item
        assert 'horario' in item

def create_restricted_image(filename):
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (100, 100), color=(0, 255, 0))  

    d = ImageDraw.Draw(img)
    d.text((10, 40), "Sem acesso", fill=(255, 0, 0))  

    img.save(filename)
