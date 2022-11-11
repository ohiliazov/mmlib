from pydantic import BaseModel


class Parameters(BaseModel):
    handicap_bar: int
    handicap_correction: int
    handicap_max: int
