from app.constants import VideoFileStatus
from app.db import get_session, Films, FilmPieces


def test_create_film(db):
    session = get_session()
    film = Films.create_film(session, name='name', description='description')
    assert film.name == 'name'
    assert film.description == 'description'
    assert film.status == VideoFileStatus.new.value
    assert film.path is None
    assert film.size is None

    film = Films.create_film(session, name='name', description='description', size=1024)
    assert film.name == 'name'
    assert film.description == 'description'
    assert film.status == VideoFileStatus.new.value
    assert film.path is None
    assert film.size == 1024


def test_get_all_films(db):
    session = get_session()
    with session.begin():
        film1 = Films.create_film(session, name='name1', description='description1')
        film1.status = VideoFileStatus.in_process.value
        film2 = Films.create_film(session, name='name2', description='description2')
        film2.status = VideoFileStatus.success.value
        film3 = Films.create_film(session, name='name3', description='description3')
        film3.status = VideoFileStatus.failed.value

    films = Films.get_all_films(session, 1, 2)
    assert len(films) == 2
    assert films[0].name == 'name2'
    assert films[1].name == 'name1'


def test_get_film(db):
    session = get_session()
    with session.begin():
        film1 = Films.create_film(session, name='name1', description='description1')
        film1.status = VideoFileStatus.in_process.value
        film2 = Films.create_film(session, name='name2', description='description2')
        film2.status = VideoFileStatus.success.value

    film = Films.get_film(session, film2.id)
    assert film.name == 'name2'
    film = Films.get_film(session, film2.id + 10000000)
    assert film is None


def test_pieces(db):
    session = get_session()

    with session.begin():
        film = Films.create_film(session, name='name', description='description')

    with session.begin():
        # TODO: add constraints for names
        FilmPieces.create_film_piece(session, film.id, 0, 10, 'blabla1')
        FilmPieces.create_film_piece(session, film.id, 2, 20, 'blabla2')
        FilmPieces.create_film_piece(session, film.id, 3, 30, 'blabla3')

    session.refresh(film)
    assert film.uploaded_size == 60
    film_pieces = session.query(FilmPieces).order_by(FilmPieces.size.asc()).all()
    assert len(film_pieces) == 3
    assert film_pieces[0].size == 10
    assert film_pieces[0].path == 'blabla1'
    assert film_pieces[1].size == 20
    assert film_pieces[1].path == 'blabla2'
    assert film_pieces[2].size == 30
    assert film_pieces[2].path == 'blabla3'
