import json
import pytest

from app.constants import VideoFileStatus
from app.config import load_config
from app.db import Films, get_session
from app.fileutils import result_storage


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
        film = Films.create_film(session, "mytest", "mydescription", size=200, status=VideoFileStatus.failed.value)

    response = client.get(f'/api/films/{film.id}')
    assert response.status_code == 200
    assert response.json == {
        'id': film.id,
        'name': "mytest",
        'description': "mydescription",
        'status': VideoFileStatus.failed.name,
        'size': 200
    }


_GET_FILM_DATA = [
    {
        'name': "mytest",
        'description': "mydescription",
        'status': VideoFileStatus.failed.name,
        'size': 200
    },
    {
        'name': "mytest2",
        'description': "mydescription2",
        'status': VideoFileStatus.in_process.name,
        'size': 400
    },
    {
        'name': "mytest3",
        'description': "mydescription3",
        'status': VideoFileStatus.success.name,
        'size': 600
    },
    {
        'name': "mytest4",
        'description': "mydescription4",
        'status': VideoFileStatus.new.name,
        'size': None
    }
]


@pytest.mark.parametrize("input_data,expected_result,status_code", [
    ({}, [_GET_FILM_DATA[3], _GET_FILM_DATA[2], _GET_FILM_DATA[1], _GET_FILM_DATA[0]], 200),
    ({'count': 1}, [_GET_FILM_DATA[3]], 200),
    ({'count': 2, 'offset': 2}, [_GET_FILM_DATA[1], _GET_FILM_DATA[0]], 200),
    ({'offset': 3}, [_GET_FILM_DATA[0]], 200),
    ({'offset': 10}, [], 200),
    ({'count': 0}, [], 400),
])
def test_get_films(client, input_data, expected_result, status_code):
    session = get_session()
    response = client.get('/api/films', query_string=input_data)
    assert response.status_code == status_code

    if status_code == 200:
        assert response.json == {"films": []}

    films = []

    with session.begin():
        films.append(Films.create_film(session, "mytest", "mydescription",
                                       size=200, status=VideoFileStatus.failed.value))
        films.append(Films.create_film(session, "mytest2", "mydescription2",
                                       size=400, status=VideoFileStatus.in_process.value))
        films.append(Films.create_film(session, "mytest3", "mydescription3",
                                       size=600, status=VideoFileStatus.success.value))
        films.append(Films.create_film(session, "mytest4", "mydescription4",
                                       size=None, status=VideoFileStatus.new.value))

    for film, data in zip(films, _GET_FILM_DATA):
        data['id'] = film.id

    response = client.get('/api/films', query_string=input_data)
    assert response.status_code == status_code

    if status_code == 200:
        assert response.json == {"films": expected_result}


@pytest.mark.parametrize("size,status,patch_data,is_same_film,status_code,expected_size,", [
    (300, VideoFileStatus.new.value, None, True, 400, 300),
    (None, VideoFileStatus.new.value, {}, True, 400, None),
    (None, VideoFileStatus.new.value, {"size": 300}, True, 200, 300),
    (400, VideoFileStatus.new.value, {"size": 600}, True, 200, 600),
    (400, VideoFileStatus.new.value, {"size": 600}, False, 404, 400),
    (400, VideoFileStatus.new.value, {"size": 600, "anything": 9999999}, True, 200, 600),
    (400, VideoFileStatus.in_process.value, {"size": 600}, True, 400, 400),
])
def test_patch_films(client, size, status, patch_data, is_same_film, status_code, expected_size):
    session = get_session()

    with session.begin():
        film = Films.create_film(session, "mytest", "desc", size=size, status=status)

    if is_same_film:
        id = film.id
    else:
        id = film.id + 1

    response = client.patch(f'/api/films/{id}', json=patch_data)
    session.refresh(film)
    assert response.status_code == status_code
    assert film.size == expected_size


@pytest.mark.parametrize("status,is_same_film,status_code", [
    (VideoFileStatus.success.value, True, 200),
    (VideoFileStatus.new.value, True, 400),
    (VideoFileStatus.in_process.value, True, 400),
    (VideoFileStatus.success.value, False, 404),
])
def test_download_film(client, status, is_same_film, status_code):
    DATA = b'test-small-data'
    FILENAME = 'name'

    result_storage.write(FILENAME, DATA)
    session = get_session()

    with session.begin():
        film = Films.create_film(session, "mytest", "desc", size=len(DATA), status=status)
        film.path = FILENAME
        session.add(film)

    if is_same_film:
        id = film.id
    else:
        id = film.id + 1

    response = client.get(f'/api/films/{id}/content')
    assert response.status_code == status_code

    if status_code == 200:
        assert response.data == DATA
