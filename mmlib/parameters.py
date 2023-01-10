from pydantic import BaseModel


class HandicapParameters(BaseModel):
    handicap_bar: int
    handicap_correction: int
    handicap_max: int
