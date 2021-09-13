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
    path = Column(String(1024), nullable=True, default=None)
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

    film_pieces = relationship("FilmPieces", lazy='joined', passive_deletes=True)

    @property
    def uploaded_size(self) -> int:
        return sum([x.size for x in self.film_pieces])

    @classmethod
    def get_all_films(cls, session: Session, offset: int, count: int) -> List["Films"]:
        query = session.query(cls).order_by(Films.id.desc())

        if offset is not None:
            query = query.offset(offset)

        if count is not None:
            query = query.limit(count)

        return query.all()

    @classmethod
    def get_film(cls, session: Session, film_id: int) -> "Films":
        return session.query(cls).filter(Films.id == film_id).one_or_none()

    @classmethod
    def create_film(cls, session: Session, name: str, description: str, size: int = None,
                    status: int = VideoFileStatus.new.value) -> "Films":
        film = cls(
            name=name,
            description=description,
            status=status,
            path=None,
            size=size
        )
        session.add(film)
        return film


class FilmPieces(Base):
    __tablename__ = "film_pieces"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'))
    number = Column(Integer)
    size = Column(Integer)
    path = Column(String(1024))

    @classmethod
    def create_film_piece(cls, session: Session, film_id: int, number: int, size: int, path: str) -> "FilmPieces":
        film_piece = cls(
            film_id=film_id,
            number=number,
            size=size,
            path=path
        )
        session.add(film_piece)
        return film_piece
