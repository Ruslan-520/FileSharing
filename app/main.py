from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import uuid
import os
from .database import get_db
from .models import File


app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Генерируем уникальный ID
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / file_id
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Записываем в БД
    db_file = File(
        id=file_id,
        filename=file.filename,
        path=str(file_path)
    )
    db.add(db_file)
    await db.commit()
    
    return {"file_id": file_id, "filename": file.filename}

@app.get("/download/{file_id}") 
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем существование записи в БД
    file_record = await db.get(File, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    file_path = Path(file_record.path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл отсутствует на диске")
    
    try:
        # Отправляем файл
        response = FileResponse(
            file_path,
            filename=file_record.filename  # Добавляем оригинальное имя файла
        )
        
        # Удаляем файл и запись из БД
        os.remove(file_path)
        await db.delete(file_record)
        await db.commit()
        
        return response
        
    except Exception as e:
        # Откатываем изменения в БД при ошибке
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке файла: {str(e)}"
        )

@app.get("/files")
async def list_files(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File))
    return [
        {
            "file_id": file.id,
            "filename": file.filename,
            "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None
        }
        for file in result.scalars()
    ]