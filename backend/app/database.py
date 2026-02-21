from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
from .config import settings 

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread" : False}
)

"""Автоматически создает сессии для каждого запроса"""
SessionLocal = sessionmaker(
                            autocommit=False, # Автосохранение каждого изменения в БД - False(Для более точного контроля с помощью ручного сохранения)
                            autoflush=False, # SQLAlchemy не отправляет запросы в БД до явного вызова flush() или commit()
                            bind=engine # Привязывает сессии к конкретному движку 
                            ) 
Base = declarative_base()

"""зависимость, которая создает новую сессию базы данных для каждого запроса и гарантированно закрывает ее после завершения запроса."""
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""Инициализация БД"""
def init_db():
    Base.metadata.create_all(bind=engine)
