from pydantic import UUID4, BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    exp: int
    sub: UUID4


class Msg(BaseModel):
    msg: str
