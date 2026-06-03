from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.photo import Photo
from pydantic import BaseModel
from typing import List
import os
import base64
from datetime import datetime
from PIL import Image
import io

router = APIRouter()

class CollageRequest(BaseModel):
    photo_ids: List[int]
    template: str  # e.g. "side-by-side", "top-bottom", "1-large-2-small", "grid", "2x2", "large-3", "5-grid"

def _load_image(file_path: str) -> Image.Image:
    """Load image from storage path."""
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # file_path is like /images/8/session_1.../file.jpg
    rel = file_path.lstrip("/").replace("images/", "", 1)
    full_path = os.path.join(backend_root, "storage", "images", rel)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Image not found: {full_path}")
    return Image.open(full_path).convert("RGB")

def _make_collage(images: List[Image.Image], template: str) -> Image.Image:
    """Stitch images into a collage based on template."""
    n = len(images)
    SIZE = 400  # cell size

    def fit(img: Image.Image, w: int, h: int) -> Image.Image:
        return img.resize((w, h), Image.LANCZOS)

    if template == "side-by-side" or (n == 2 and template not in ("top-bottom",)):
        canvas = Image.new("RGB", (SIZE * 2, SIZE))
        canvas.paste(fit(images[0], SIZE, SIZE), (0, 0))
        canvas.paste(fit(images[1], SIZE, SIZE), (SIZE, 0))

    elif template == "top-bottom":
        canvas = Image.new("RGB", (SIZE, SIZE * 2))
        canvas.paste(fit(images[0], SIZE, SIZE), (0, 0))
        canvas.paste(fit(images[1], SIZE, SIZE), (0, SIZE))

    elif template == "1-large-2-small" and n >= 3:
        # Left: large, Right: two stacked
        canvas = Image.new("RGB", (SIZE * 2, SIZE * 2))
        canvas.paste(fit(images[0], SIZE * 2, SIZE * 2), (0, 0))
        canvas.paste(fit(images[1], SIZE, SIZE), (SIZE * 2 - SIZE, 0))
        canvas.paste(fit(images[2], SIZE, SIZE), (SIZE * 2 - SIZE, SIZE))
        # Redo: left large, right column two small
        canvas = Image.new("RGB", (SIZE * 2, SIZE * 2))
        canvas.paste(fit(images[0], SIZE, SIZE * 2), (0, 0))
        canvas.paste(fit(images[1], SIZE, SIZE), (SIZE, 0))
        canvas.paste(fit(images[2], SIZE, SIZE), (SIZE, SIZE))

    elif template == "grid" and n >= 3:
        # 3-image grid: top full-width, bottom two
        canvas = Image.new("RGB", (SIZE * 2, SIZE * 2))
        canvas.paste(fit(images[0], SIZE * 2, SIZE), (0, 0))
        canvas.paste(fit(images[1], SIZE, SIZE), (0, SIZE))
        canvas.paste(fit(images[2], SIZE, SIZE), (SIZE, SIZE))

    elif template == "2x2" or (n == 4 and template not in ("large-3",)):
        canvas = Image.new("RGB", (SIZE * 2, SIZE * 2))
        positions = [(0, 0), (SIZE, 0), (0, SIZE), (SIZE, SIZE)]
        for i, pos in enumerate(positions[:n]):
            canvas.paste(fit(images[i], SIZE, SIZE), pos)

    elif template == "large-3" and n >= 4:
        # Top large, bottom three
        canvas = Image.new("RGB", (SIZE * 3, SIZE * 2))
        canvas.paste(fit(images[0], SIZE * 3, SIZE), (0, 0))
        for i in range(1, min(4, n)):
            canvas.paste(fit(images[i], SIZE, SIZE), ((i - 1) * SIZE, SIZE))

    elif template == "5-grid" or n == 5:
        # Top row: 3, bottom row: 2 centered
        canvas = Image.new("RGB", (SIZE * 3, SIZE * 2))
        for i in range(min(3, n)):
            canvas.paste(fit(images[i], SIZE, SIZE), (i * SIZE, 0))
        offsets = [SIZE // 2, SIZE // 2 + SIZE]
        for i, x in enumerate(offsets):
            if 3 + i < n:
                canvas.paste(fit(images[3 + i], SIZE, SIZE), (x, SIZE))

    else:
        # Fallback: horizontal strip
        canvas = Image.new("RGB", (SIZE * n, SIZE))
        for i, img in enumerate(images):
            canvas.paste(fit(img, SIZE, SIZE), (i * SIZE, 0))

    return canvas


@router.post("/create")
def create_collage(
    request: CollageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    n = len(request.photo_ids)
    if n < 2 or n > 5:
        raise HTTPException(status_code=400, detail="Select between 2 and 5 photos")

    # Fetch photos — must belong to current user
    photos = db.query(Photo).filter(
        Photo.id.in_(request.photo_ids),
        Photo.user_id == current_user.id
    ).all()

    if len(photos) != n:
        raise HTTPException(status_code=404, detail="One or more photos not found")

    # Load images
    try:
        images = [_load_image(p.file_path) for p in photos]
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Generate collage
    collage = _make_collage(images, request.template)

    # Save collage to storage
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    collage_dir = os.path.join(backend_root, "storage", "images", str(current_user.id), "collages")
    os.makedirs(collage_dir, exist_ok=True)

    filename = f"collage_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    full_path = os.path.join(collage_dir, filename)
    collage.save(full_path, "JPEG", quality=90)

    web_path = f"/images/{current_user.id}/collages/{filename}"

    # Insert Photo record
    login_session_id = current_user.login_session_id or "collage"
    photo_record = Photo(
        user_id=current_user.id,
        session_id=login_session_id,
        file_path=web_path,
        source="collage",
        is_best_in_session=False,
        created_at=datetime.utcnow()
    )
    db.add(photo_record)
    db.commit()
    db.refresh(photo_record)

    return {
        "id": photo_record.id,
        "file_path": web_path,
        "source": "collage",
        "created_at": photo_record.created_at.isoformat()
    }
