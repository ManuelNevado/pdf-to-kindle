"""Verificación de dependencias externas y configuración."""

import shutil
import sys


KINDLE_6_WIDTH = 560
KINDLE_6_HEIGHT = 735

DEPENDENCIES = {
    "ebook-convert": {
        "name": "Calibre (ebook-convert)",
        "url": "https://calibre-ebook.com/download",
        "help": (
            "Instala Calibre desde https://calibre-ebook.com/download\n"
            "En Windows, asegúrate de que la carpeta de Calibre esté en el PATH.\n"
            "En Linux: sudo apt install calibre"
        ),
    },
    "k2pdfopt": {
        "name": "k2pdfopt",
        "url": "https://www.willus.com/k2pdfopt/",
        "help": (
            "Descarga k2pdfopt desde https://www.willus.com/k2pdfopt/\n"
            "Coloca el ejecutable en una carpeta del PATH.\n"
            "En Linux también puedes compilar desde el código fuente."
        ),
    },
    "ocrmypdf": {
        "name": "OCRmyPDF",
        "url": "https://ocrmypdf.readthedocs.io/",
        "help": (
            "pip install ocrmypdf\n"
            "También necesitas Tesseract OCR:\n"
            "  Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "  Linux: sudo apt install tesseract-ocr tesseract-ocr-spa\n"
            "  macOS: brew install tesseract tesseract-lang"
        ),
    },
}


def check_dependency(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def check_all_dependencies(require_ocr: bool = False) -> dict[str, bool]:
    results = {}
    for cmd in DEPENDENCIES:
        if cmd == "ocrmypdf" and not require_ocr:
            continue
        results[cmd] = check_dependency(cmd)
    return results


def print_missing_dependencies(results: dict[str, bool]) -> bool:
    missing = [cmd for cmd, found in results.items() if not found]
    if not missing:
        return True
    print("\n⚠  Faltan dependencias externas:\n")
    for cmd in missing:
        dep = DEPENDENCIES[cmd]
        print(f"  ✗ {dep['name']}")
        print(f"    {dep['help']}\n")
    return False


def ensure_dependencies(need_ocr: bool = False) -> None:
    results = check_all_dependencies(require_ocr=need_ocr)
    if not print_missing_dependencies(results):
        sys.exit(1)
