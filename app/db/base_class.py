from datetime import UTC, datetime

from sqlmodel import SQLModel, Field


class Base(SQLModel):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(tz=UTC), sa_column_kwargs={"db_default": "now()"})
    updated_at: datetime = Field(default=datetime.now(tz=UTC), sa_column_kwargs={"db_default": "now()"})


