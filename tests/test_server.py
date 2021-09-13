import json
import pytest

from app.constants import VideoFileStatus
from app.config import load_config
from app.db import Films, get_session


def test_check_not_found(client):
    response = client.get('/strange')
    assert response.status_code == 404
    assert response.json == {
        "code": 404,
        "description":"The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
        "name":"Not Found"
    }


def test_correct_create_film(client):
    # Validation
    data = {
        "name": "my name",
        "description": "my description",
        "size": 300000
    }

    response = client.post('/api/films', json=data)
    data = response.json
    assert response.status_code == 200
    assert data['name'] == 'my name'
    assert data['description'] == 'my description'
    assert data['size'] == 300000

    session = get_session()
    films = session.query(Films).all()
    assert len(films) == 1
    assert films[0].id == data['id']
    assert films[0].name == data['name']
    assert films[0].description == data['description']
    assert films[0].status == VideoFileStatus.new.value


@pytest.mark.parametrize("data", [
    {},
    {'name': '321312'},
    {'descroption': '321312'},
    {'name': 'A', 'descroption': 'B', 'size': 'C'},
    None
])
def test_incorrect_create_film(client, data):
    response = client.post('/api/films', json=data)
    assert response.status_code == 400


def test_get_film(client):
    response = client.get('/api/films/22222')
    assert response.status_code == 404
    session = get_session()
    with session.begin():
        film = Films.create_film(session, "mytest", "mydescription", 200)
        film.status = VideoFileStatus.failed.value
        session.add(film)

    response = client.get(f'/api/films/{film.id}')
    assert response.status_code == 200
    assert response.json == {
        'id': film.id,
        'name': "mytest",
        'description': "mydescription",
        'status': VideoFileStatus.failed.name,
        'size': 200
    }
