from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

from app.constants import VideoFileStatus

def _get_engine_settings():
    return 'sqlite:///sql.db', {}

db_path, engine_settings = _get_engine_settings()
engine = create_engine(db_path, **engine_settings)

Base = declarative_base()
Session = sessionmaker(bind=engine)


def get_session():
    return Session()


class Films(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    description = Column(String(4096))
    status = Column(Integer)
    path = Column(String(1024))
    file_size = Column(Integer)
    size = Column(Integer, nullable=True, default=None)

    def as_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': VideoFileStatus(self.status).name,
            'size': self.size
        }
        return result

class FilmPieces(Base):
    __tablename__ = "film_pieces"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'))
    piece_number = Column(Integer)
    piece_size = Column(Integer)
    path = Column(String(1024))


# TODO: move session to server
def create_film_pieces(session, film_id, piece_number, piece_size, path):
    session = get_session()
    film_piece = FilmPieces(
        film_id=film_id,
        piece_number=piece_number,
        piece_size=piece_size,
        path=path
    )
    session.add(film_piece)
    session.commit()
    return film_piece


def get_all_films(session):
    return session.query(Films).order_by(Films.id.desc()).all()


def get_film(session, film_id):
    return session.query(Films).filter(Films.id == film_id).one_or_none()


def create_new_film(session, name, description, size=None):
    film = Films(
        name=name,
        description=description,
        status=VideoFileStatus.new.value,
        path="",
        size=size
    )
    session.add(film)
    return film
