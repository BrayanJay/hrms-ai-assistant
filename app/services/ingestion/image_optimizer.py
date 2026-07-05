from io import BytesIO
from base64 import b64encode
from PIL import Image
from app.core.config import settings

async def optimise_image(image_bytes: bytes) -> str:
    max_size = settings.max_image_size
    img_quality = 85

    img =  Image.open(BytesIO(image_bytes))
    img = img.convert("RGB")
    ratio = min(max_size/img.width, max_size/img.height)
    new_size = (int(img.width*ratio), int(img.height*ratio))
    img = img.resize(new_size)

    buf = BytesIO()
    img.save(buf, format="WebP", quality=img_quality)
    while buf.tell() > 400 * 1024 and img_quality > 10:
            img_quality -= 10
            buf = BytesIO()
            img.save(buf, format="WebP", quality=img_quality)

    image_bytes = buf.getvalue()
    return "data:image/webp;base64," + b64encode(image_bytes).decode("utf-8")