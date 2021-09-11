from typing import Optional
from pydantic import BaseModel, constr, PositiveInt, NonNegativeInt


class GetListSchema(BaseModel):
    start: Optional[NonNegativeInt] = 0
    count: Optional[PositiveInt] = 100


class CreateFilmSchema(BaseModel):
    name: constr(min_length=1)
    description: constr(min_length=1)
    size: Optional[PositiveInt] = None


class PatchFilmSchema(BaseModel):
    size: PositiveInt


class PutVideoSchema(BaseModel):
    piece_number: NonNegativeInt
    piece_content: constr(min_length=1)
