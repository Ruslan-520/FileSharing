from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid

class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullabel=False )
    path = Column(String(512), unique=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_downloaded = Column(Boolean, default=False)

