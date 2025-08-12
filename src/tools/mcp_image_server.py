import base64
import os, io, time, re
import sys
import logging
from typing import Literal, Optional
from PIL import Image as PILImage, ImageDraw, ImageFont
from mcp.server.fastmcp import FastMCP, Image
from dotenv import load_dotenv
from random import Random
from openai import OpenAI

load_dotenv()

mcp = FastMCP("ImageGen")

logging.basicConfig(stream=sys.stderr, level=logging.info, format="[image_server] %(levelname)s: %(message)s")

def _safe_filename(txt: str) -> str:
    txt = re.sub(r"[^a-zA-Z0-9-_]+", "_", txt.strip())[:40]
    return txt or f"img_{int(time.time())}"

def _pil_placeholder(prompt: str, size: str, seed: Optional[int]) -> bytes:
    w, h = map(int, size.split("x"))
    img = PILImage.new("RGB", (w, h))

    rnd = Random(seed if seed is not None else (hash(prompt + size) & 0xFFFFFFFF))
    base_r = rnd.randint(40, 180)
    base_g = rnd.randint(40, 180)
    base_b = rnd.randint(40, 180)

    for y in range(h):
        c = int(255 * y / max(1, h-1))
        for x in range(w):
            img.putpixel((x, y), ((base_r + c) % 256, (base_g + c//2) % 256, (base_b + c//3) % 256))
    
    draw = ImageDraw.Draw(img)
    
    try: 
        font = ImageFont.load_default()
    except Exception:
        font = None
    
    draw.text((20, 20), prompt[:120], fill=(255, 255, 255), font=font, spacing=4)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@mcp.tool()
def generate_image(
    prompt: str,
    size: Literal["512x512", "768x768", "1024x1024"] = "1024x1024",
    style: Literal["digital-art","photorealistic","anime","watercolor"] = "digital-art",
    seed: Optional[int] = 0,
    filename: Optional[str] = None,
) -> list:
    """
    Generates an image from a prompt and returns:
    - an image block
    - info about the generated image
    """
    data: bytes | None = None

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is not None:
            client = OpenAI(api_key=api_key)
            full_prompt = f"{prompt}\nStyle: {style}\nSize: {size}"
            response = client.images.generate(model="gpt-image-1", prompt=full_prompt, size=size)
            b64 = response.data[0].b64_json
            data = base64.b64decode(b64)
        else:
            logging.info("OPENAI_API_KEY not set. Falling back to placeholder")
    except Exception as e:
        data = None
        logging.error(f"Image generation failed: {e}")

    if data is None:
        data = _pil_placeholder(prompt, size, seed)
    
    out_dir = os.environ.get("IMG_OUT", "generated")
    os.makedirs(out_dir, exist_ok=True)
    name = filename or _safe_filename(prompt)
    path = os.path.join(out_dir, f"{name}.png")

    with open(path, "wb") as f:
        f.write(data)

    return [Image(data=data, format="png"), f"saved_path={path}"]

if __name__ == "__main__":
    mcp.run(transport="stdio")
