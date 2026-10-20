"""Módulos de conversión: texto (EPUB), maquetado (k2pdfopt), OCR, DOCX."""

import subprocess
from pathlib import Path

from .config import KINDLE_6_WIDTH, KINDLE_6_HEIGHT


def convert_to_epub(input_path: Path, output_dir: Path) -> Path:
    """Convierte a EPUB usando ebook-convert de Calibre."""
    output_path = output_dir / (input_path.stem + ".epub")
    cmd = [
        "ebook-convert",
        str(input_path),
        str(output_path),
        "--output-profile", "kindle",
        "--change-justification", "justify",
        "--enable-heuristics",
    ]
    print(f"  Convirtiendo a EPUB: {input_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ebook-convert falló para {input_path.name}:\n{result.stderr}"
        )
    print(f"  ✓ Generado: {output_path.name}")
    return output_path


def convert_with_k2pdfopt(
    input_path: Path,
    output_dir: Path,
    landscape: bool = False,
    crop_margins: bool = True,
) -> Path:
    """Convierte PDF con k2pdfopt optimizado para Kindle 6"."""
    output_path = output_dir / (input_path.stem + "_k2.pdf")
    cmd = [
        "k2pdfopt",
        str(input_path),
        "-o", str(output_path),
        "-dev", "kp3",          # Perfil Kindle Paperwhite (6")
        "-w", str(KINDLE_6_WIDTH),
        "-h", str(KINDLE_6_HEIGHT),
        "-dpi", "167",          # DPI nativo del Kindle 6"
        "-j", "0",              # Sin justificación extra
        "-wrap+",               # Re-flow de texto
        "-ui-",                 # Sin interacción
        "-x",                   # Salir al terminar
    ]

    if crop_margins:
        cmd.extend(["-m", "0.2"])  # Recorte de márgenes agresivo

    if landscape:
        cmd.extend(["-ls"])  # Modo paisaje → dividir página

    print(f"  Optimizando maquetado: {input_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"k2pdfopt falló para {input_path.name}:\n{result.stderr}"
        )
    print(f"  ✓ Generado: {output_path.name}")
    return output_path


def run_ocr(input_path: Path, output_dir: Path, language: str = "spa") -> Path:
    """Aplica OCR con OCRmyPDF (por defecto en español)."""
    output_path = output_dir / (input_path.stem + "_ocr.pdf")
    cmd = [
        "ocrmypdf",
        "-l", language,
        "--rotate-pages",
        "--deskew",
        "--clean",
        "--force-ocr",
        str(input_path),
        str(output_path),
    ]
    print(f"  Aplicando OCR ({language}): {input_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"OCRmyPDF falló para {input_path.name}:\n{result.stderr}"
        )
    print(f"  ✓ OCR completado: {output_path.name}")
    return output_path


def convert_docx_to_pdf(input_path: Path, output_dir: Path) -> Path:
    """Convierte DOCX a PDF usando ebook-convert como paso intermedio."""
    pdf_path = output_dir / (input_path.stem + ".pdf")
    cmd = [
        "ebook-convert",
        str(input_path),
        str(pdf_path),
    ]
    print(f"  Convirtiendo DOCX a PDF: {input_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ebook-convert falló para {input_path.name}:\n{result.stderr}"
        )
    return pdf_path


def process_file(
    input_path: Path,
    output_dir: Path,
    mode: str = "auto",
    landscape: bool = False,
    ocr_language: str = "spa",
) -> Path:
    """Procesa un archivo según el modo indicado. Devuelve la ruta del resultado."""
    from .detector import analyze_pdf

    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = input_path.suffix.lower()

    # Si es DOCX, primero decidir: modo texto → EPUB directo, otro modo → convertir a PDF
    if suffix == ".docx":
        if mode in ("auto", "texto"):
            return convert_to_epub(input_path, output_dir)
        else:
            input_path = convert_docx_to_pdf(input_path, output_dir)
            suffix = ".pdf"

    if suffix != ".pdf":
        raise ValueError(f"Formato no soportado: {suffix}")

    # Modo auto: analizar el PDF
    if mode == "auto":
        analysis = analyze_pdf(input_path)
        print(f"  Análisis: {analysis}")
        mode = analysis.recommended_mode()
        if analysis.has_landscape_pages and not landscape:
            landscape = True
            print("  → Detectadas páginas horizontales, activando modo paisaje")

    # Modo OCR: aplicar OCR y luego convertir a EPUB
    if mode == "ocr":
        ocr_path = run_ocr(input_path, output_dir, ocr_language)
        return convert_to_epub(ocr_path, output_dir)

    # Modo texto: convertir a EPUB
    if mode == "texto":
        return convert_to_epub(input_path, output_dir)

    # Modo maquetado: k2pdfopt
    if mode == "maquetado":
        return convert_with_k2pdfopt(input_path, output_dir, landscape=landscape)

    raise ValueError(f"Modo desconocido: {mode}")
