from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel
import io
import os
from typing import List
from .database import get_db
from .models import User, Meme
from .auth import get_current_user


class TextItem(BaseModel):
    text: str
    alignment: str = "center"  # "top", "center", "bottom"

class MemeTextRequest(BaseModel):
    texts: List[TextItem]

router = APIRouter(prefix="/api/memes", tags=["memes"])

UPLOAD_DIR = "/app/uploads"
OUTPUT_DIR = "/app/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Загрузка изображения для создания мема"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Сохраняем оригинальное изображение
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Создаем запись в БД
    meme = Meme(
        user_id=current_user.id,
        filename=file_path,
        original_filename=file.filename
    )
    db.add(meme)
    db.commit()
    db.refresh(meme)

    return {
        "id": meme.id,
        "filename": meme.original_filename,
        "message": "Image uploaded successfully"
    }


@router.post("/create/{meme_id}")
async def create_meme(
    meme_id: int,
    request: MemeTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание мема с текстом поверх изображения"""
    meme = db.query(Meme).filter(
        Meme.id == meme_id,
        Meme.user_id == current_user.id
    ).first()

    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    # Открываем изображение
    try:
        image = Image.open(meme.filename)
        draw = ImageDraw.Draw(image)

        # Пытаемся загрузить шрифт, если не получается - используем стандартный
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()

        # Добавляем текст на изображение
        texts = request.texts
        width, height = image.size
        
        # Фильтруем только непустые тексты
        valid_texts = [t for t in texts if t.text.strip()]
        
        if not valid_texts:
            raise HTTPException(status_code=400, detail="No valid texts provided")
        
        # Группируем тексты по выравниванию
        top_texts = [t for t in valid_texts if t.alignment.lower() == "top"]
        center_texts = [t for t in valid_texts if t.alignment.lower() == "center"]
        bottom_texts = [t for t in valid_texts if t.alignment.lower() == "bottom"]
        
        # Распределяем тексты по вертикали в зависимости от выравнивания
        for text_item in valid_texts:
            text = text_item.text.strip()
            alignment = text_item.alignment.lower()
            
            # Получаем размеры текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height_bbox = bbox[3] - bbox[1]
            
            # Выравнивание по горизонтали (всегда по центру)
            x_position = (width - text_width) // 2
            
            # Выравнивание по вертикали
            if alignment == "top":
                # Верх - тексты размещаются сверху вниз
                index = top_texts.index(text_item)
                if len(top_texts) == 1:
                    y_position = 20  # Отступ сверху
                else:
                    spacing = min(30, (height // 3) // len(top_texts))
                    y_position = 20 + (text_height_bbox + spacing) * index
            elif alignment == "bottom":
                # Низ - тексты размещаются снизу вверх
                index = bottom_texts.index(text_item)
                if len(bottom_texts) == 1:
                    y_position = height - text_height_bbox - 20  # Отступ снизу
                else:
                    spacing = min(30, (height // 3) // len(bottom_texts))
                    y_position = height - text_height_bbox - 20 - (text_height_bbox + spacing) * (len(bottom_texts) - 1 - index)
            else:  # center (по умолчанию)
                # Центр - тексты размещаются в центре изображения
                index = center_texts.index(text_item)
                center_y = height // 2
                if len(center_texts) == 1:
                    y_position = center_y - text_height_bbox // 2
                else:
                    total_height = (text_height_bbox + 20) * len(center_texts)
                    start_y = center_y - total_height // 2
                    y_position = start_y + (text_height_bbox + 20) * index

            # Рисуем обводку (черная)
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text(
                        (x_position + adj, y_position + adj2),
                        text,
                        font=font,
                        fill="black"
                    )
            
            # Рисуем основной текст (белый)
            draw.text(
                (x_position, y_position),
                text,
                font=font,
                fill="white"
            )

        # Сохраняем результат
        output_filename = f"meme_{meme_id}_{current_user.id}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        image.save(output_path, "PNG")

        return {
            "id": meme_id,
            "output_filename": output_filename,
            "message": "Meme created successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating meme: {str(e)}")


@router.get("/download/{meme_id}")
async def download_meme(
    meme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Скачивание созданного мема"""
    meme = db.query(Meme).filter(
        Meme.id == meme_id,
        Meme.user_id == current_user.id
    ).first()

    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    output_filename = f"meme_{meme_id}_{current_user.id}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Meme file not found")

    return FileResponse(
        output_path,
        media_type="image/png",
        filename=f"meme_{meme.original_filename}"
    )


@router.get("/image/{meme_id}")
async def get_meme_image(
    meme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение изображения мема для отображения на сайте"""
    meme = db.query(Meme).filter(
        Meme.id == meme_id,
        Meme.user_id == current_user.id
    ).first()

    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    output_filename = f"meme_{meme_id}_{current_user.id}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Определяем тип медиа на основе расширения файла
    def get_media_type(filename):
        ext = os.path.splitext(filename)[1].lower()
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return media_types.get(ext, 'image/png')

    # Если готовый мем не существует, возвращаем оригинальное изображение
    if not os.path.exists(output_path):
        if os.path.exists(meme.filename):
            return FileResponse(
                meme.filename,
                media_type=get_media_type(meme.filename),
            )
        raise HTTPException(status_code=404, detail="Meme file not found")

    return FileResponse(
        output_path,
        media_type="image/png",
    )


@router.get("/list")
async def list_memes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Список всех мемов пользователя"""
    memes = db.query(Meme).filter(Meme.user_id == current_user.id).all()
    result = []
    for meme in memes:
        output_filename = f"meme_{meme.id}_{current_user.id}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        has_meme = os.path.exists(output_path)
        
        result.append({
            "id": meme.id,
            "filename": meme.original_filename,
            "created_at": meme.created_at.isoformat(),
            "has_meme": has_meme  # Есть ли готовый мем
        })
    return result

