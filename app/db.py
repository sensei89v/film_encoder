from typing import Dict, List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.constants import VideoFileStatus
from app.config import load_config

_config = load_config()

db_path = _config['database']
engine = create_engine(db_path)

Base = declarative_base()
Session = sessionmaker(bind=engine, autocommit=True)


def get_session() -> Session:
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

    def as_dict(self) -> Dict:
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': VideoFileStatus(self.status).name,
            'size': self.size
        }
        return result

    # TODO: orm lazy load
    film_pieces = relationship("FilmPieces", lazy='joined', passive_deletes=True)

    @property
    def uploaded_size(self) -> int:
        return sum([x.piece_size for x in self.film_pieces])


class FilmPieces(Base):
    __tablename__ = "film_pieces"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'))
    piece_number = Column(Integer)
    piece_size = Column(Integer)
    path = Column(String(1024))


# TODO: move session to server
def create_film_pieces(session: Session, film_id: int, piece_number: int, piece_size: int, path: str) -> FilmPieces:
    film_piece = FilmPieces(
        film_id=film_id,
        piece_number=piece_number,
        piece_size=piece_size,
        path=path
    )
    session.add(film_piece)
    return film_piece


def get_all_films(session: Session, start: int, count: int) -> List[Films]:
    query = session.query(Films).order_by(Films.id.desc())

    if start is not None:
        query = query.offset(start)

    if count is not None:
        query = query.limit(count)

    return query.all()


def get_film(session: Session, film_id: int) -> Films:
    return session.query(Films).filter(Films.id == film_id).one_or_none()


def create_new_film(session: Session, name: str, description: str, size: int = None) -> Films:
    film = Films(
        name=name,
        description=description,
        status=VideoFileStatus.new.value,
        path="",
        size=size
    )
    session.add(film)
    return film
