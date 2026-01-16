from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 确保 data 目录存在，通常 docker-compose 会挂载这个目录
SQLALCHEMY_DATABASE_URL = "sqlite:////app/data/horizon.db"
# Local dev fallback if /app/data doesn't exist (though code implies docker usage)
# SQLALCHEMY_DATABASE_URL = "sqlite:///./data/horizon.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
