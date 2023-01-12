from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from app.db.base_class import BaseModel


class User(BaseModel):
    external_id = Column(
        UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
        default=uuid4,
        server_default=func.uuid_generate_v4(),
    )
    email = Column(EmailType, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)
    roles = relationship(
        "Role",
        viewonly=True,
        secondary="userrole",
        lazy="joined",
        uselist=True,
    )

    def __repr__(self):
        return f"{self.id} - {self.email}"


class Role(BaseModel):
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"{self.id} - {self.name}"


class UserRole(BaseModel):
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    role_id = Column(BigInteger, ForeignKey("role.id"), nullable=False)

    def __repr__(self):
        return f"{self.id} - {self.user_id} - {self.role_id}"
