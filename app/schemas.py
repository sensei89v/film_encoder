from typing import Optional
from pydantic import BaseModel, constr, PositiveInt, NonNegativeInt, conint

from app.config import load_config

_config = load_config()

MAX_FILE_SIZE = _config['max_film_size']


class GetListSchema(BaseModel):
    start: Optional[NonNegativeInt] = 0
    count: Optional[PositiveInt] = 100


class CreateFilmSchema(BaseModel):
    name: constr(min_length=1)
    description: constr(min_length=1)
    size: Optional[conint(ge=0, le=MAX_FILE_SIZE)] = None


class PatchFilmSchema(BaseModel):
    size: conint(ge=0, le=MAX_FILE_SIZE)


class PutVideoSchema(BaseModel):
    number: NonNegativeInt
    content: constr(min_length=1)
