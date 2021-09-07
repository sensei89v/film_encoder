from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

from constants import VideoFileStatus

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

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        result['status'] = VideoFileStatus(result['status']).name
        return result

def get_all_films():
    session = get_session()
    return session.query(Films).order_by(Films.id.desc()).all()


def get_film(film_id):
    session = get_session()
    return session.query(Films).filter(Films.id == film_id).one_or_none()


def create_new_film(name, description):
    session = get_session()
    film = Films(
        name=name,
        description=description,
        status=VideoFileStatus.new.value,
        path=""
    )
    session.add(film)
    session.commit()
    return film.as_dict()
