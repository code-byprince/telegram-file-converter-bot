import os
import img2pdf
from PIL import Image
from pdf2image import convert_from_path


def convert_image_format(input_path: str, output_path: str, target_format: str):
    """JPG/PNG/WEBP/BMP wagera ke beech convert karta hai."""
    img = Image.open(input_path)
    if target_format.lower() in ("jpg", "jpeg") and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(output_path, format=target_format.upper() if target_format.lower() != "jpg" else "JPEG")
    return output_path


def compress_image(input_path: str, output_path: str, quality: int = 50):
    """Image ka size chhota karta hai (quality 1-95, kam quality = zyada compression)."""
    img = Image.open(input_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(output_path, format="JPEG", quality=quality, optimize=True)
    return output_path


def images_to_pdf(image_paths: list, output_path: str):
    """Ek ya multiple images ko ek PDF me convert karta hai."""
    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(image_paths))
    return output_path


def pdf_to_images(pdf_path: str, output_dir: str) -> list:
    """PDF ke har page ko PNG image banata hai. Returns list of image paths."""
    pages = convert_from_path(pdf_path, dpi=150)
    output_paths = []
    for i, page in enumerate(pages, start=1):
        out_path = os.path.join(output_dir, f"page_{i}.png")
        page.save(out_path, "PNG")
        output_paths.append(out_path)
    return output_paths


def resize_image(input_path: str, output_path: str, width: int, height: int):
    """Image ko diye gaye width x height me resize karta hai."""
    img = Image.open(input_path)
    resized = img.resize((width, height))
    if output_path.lower().endswith((".jpg", ".jpeg")) and resized.mode in ("RGBA", "P"):
        resized = resized.convert("RGB")
    resized.save(output_path)
    return output_path
