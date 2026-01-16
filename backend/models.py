from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    face_encodings = relationship("FaceEncoding", back_populates="user")
    recognition_logs = relationship("RecognitionLog", back_populates="user")

class FaceEncoding(Base):
    """Stores the 128-d face encoding vector as a pickled blob"""
    __tablename__ = "face_encodings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    encoding = Column(PickleType, nullable=False) # Stores numpy array
    created_at = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", back_populates="face_encodings")

class RecognitionLog(Base):
    __tablename__ = "recognition_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Null if unknown/guest
    user_name_snapshot = Column(String) # Store name at time of recognition for convenience
    timestamp = Column(DateTime, default=datetime.datetime.now)
    image_path = Column(String, nullable=True) # Optional path to saved image

    user = relationship("User", back_populates="recognition_logs")
