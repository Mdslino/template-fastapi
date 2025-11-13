"""
Pydantic schemas for API request/response models.

This module defines common Pydantic models used across the API for
authentication and general responses.
"""

from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    """
    JWT token response schema.

    Attributes:
        access_token: The JWT access token
        token_type: Token type (default: 'bearer')
    """

    access_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    """
    JWT token payload schema.

    Attributes:
        exp: Token expiration timestamp
        sub: Subject (user UUID)
    """

    exp: int
    sub: UUID


class Msg(BaseModel):
    """
    Generic message response schema.

    Attributes:
        msg: Message text
    """

    msg: str
