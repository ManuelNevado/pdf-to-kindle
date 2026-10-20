"""Análisis de PDFs: detectar si es escaneado, si tiene maquetación compleja, etc."""

from pathlib import Path

import fitz  # PyMuPDF


def count_text_chars(page: fitz.Page) -> int:
    return len(page.get_text("text").strip())


def has_images(page: fitz.Page) -> bool:
    return len(page.get_images(full=True)) > 0


def has_tables_or_complex_layout(page: fitz.Page) -> bool:
    """Heurística: muchos bloques de texto dispersos o imágenes grandes → maquetación compleja."""
    blocks = page.get_text("dict")["blocks"]
    image_blocks = [b for b in blocks if b["type"] == 1]
    text_blocks = [b for b in blocks if b["type"] == 0]

    if len(image_blocks) >= 2:
        return True

    if len(text_blocks) >= 6:
        xs = sorted(set(round(b["bbox"][0], -1) for b in text_blocks))
        if len(xs) >= 3:
            return True

    return False


def is_landscape(page: fitz.Page) -> bool:
    rect = page.rect
    return rect.width > rect.height


class PDFAnalysis:
    def __init__(
        self,
        path: Path,
        is_scanned: bool,
        is_complex_layout: bool,
        has_landscape_pages: bool,
        total_pages: int,
    ):
        self.path = path
        self.is_scanned = is_scanned
        self.is_complex_layout = is_complex_layout
        self.has_landscape_pages = has_landscape_pages
        self.total_pages = total_pages

    def recommended_mode(self) -> str:
        if self.is_scanned:
            return "ocr"
        if self.is_complex_layout:
            return "maquetado"
        return "texto"

    def __str__(self) -> str:
        flags = []
        if self.is_scanned:
            flags.append("escaneado")
        if self.is_complex_layout:
            flags.append("maquetación compleja")
        if self.has_landscape_pages:
            flags.append("páginas horizontales")
        desc = ", ".join(flags) if flags else "texto simple"
        return f"{self.path.name}: {desc} ({self.total_pages} págs) → modo recomendado: {self.recommended_mode()}"


def analyze_pdf(path: Path, sample_pages: int = 10) -> PDFAnalysis:
    doc = fitz.open(path)
    total = len(doc)
    step = max(1, total // sample_pages)
    pages_to_check = range(0, total, step)

    scanned_count = 0
    complex_count = 0
    landscape_count = 0

    for i in pages_to_check:
        page = doc[i]
        chars = count_text_chars(page)
        imgs = has_images(page)

        if chars < 50 and imgs:
            scanned_count += 1

        if has_tables_or_complex_layout(page):
            complex_count += 1

        if is_landscape(page):
            landscape_count += 1

    checked = len(list(pages_to_check))
    threshold = checked * 0.5

    return PDFAnalysis(
        path=path,
        is_scanned=scanned_count > threshold,
        is_complex_layout=complex_count > threshold,
        has_landscape_pages=landscape_count > threshold,
        total_pages=total,
    )
