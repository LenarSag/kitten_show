from uuid import UUID

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description='Access token')
    token_type: str = Field(..., description='Token type')


class TokenData(BaseModel):
    user_id: UUID = Field(..., description='User id')
