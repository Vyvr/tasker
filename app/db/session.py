from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL, ENVIRONMENT


engine = create_engine(DATABASE_URL)

if ENVIRONMENT == "dev":
    engine.echo = True
else:
    engine.echo = False

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
