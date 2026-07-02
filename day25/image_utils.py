import base64
from PIL import Image
import io

def encode_image(path: str, max_dim: int = 1568)-> tuple[str,str]:
    
    img = Image.open(path)
    img.thumbnail((max_dim, max_dim))
    buf = io.BytesIO()
    fmt = "JPEG" if img.mode != "RGBA" else "PNG"
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg"
    return b64, mime