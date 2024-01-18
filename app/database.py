# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:modric19@localhost:5432/users"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:modric19@localhost:5432/users"

engine = create_engine(SQLALCHEMY_DATABASE_URL)



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

Base = declarative_base()
