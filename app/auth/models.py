from uuid import uuid4

from sqlalchemy import Boolean, Column, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import EmailType

from app.core.security import get_password_hash, verify_password
from app.db.base_class import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    external_id = Column(
        UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
        default=uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    email = Column(EmailType, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    def set_password(self, password: str) -> None:
        self.hashed_password = get_password_hash(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)
