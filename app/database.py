from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

#настройки подключения 
DB_URL = "postgresql+asyncpg://postgres:12345@db:5432/filesharing"

#1.создаем движок для работы с бд
engine = create_async_engine(DB_URL)

#2.Создаем сесси
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

#3.Базовый класс для моделей
Base = declarative_base()

#4.Функция для получения сесси
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
        await db.commit()
        
    except:
        await db.rollback()
        raise
    finally:
        await db.close()