"""Interfaz de línea de comandos."""

import argparse
import shutil
import sys
from pathlib import Path

from .config import ensure_dependencies
from .converter import process_file
from .mailer import send_to_kindle


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def copy_to_kindle_usb(files: list[Path], kindle_path: Path) -> None:
    if not kindle_path.exists():
        raise FileNotFoundError(
            f"No se encuentra la ruta del Kindle: {kindle_path}\n"
            f"  Conecta el Kindle por USB y comprueba la letra de unidad."
        )
    kindle_path.mkdir(parents=True, exist_ok=True)
    print(f"\n📂 Copiando {len(files)} archivo(s) a {kindle_path}...")
    for f in files:
        dest = kindle_path / f.name
        shutil.copy2(f, dest)
        print(f"  ✓ {f.name}")
    print("  Listo. Expulsa el Kindle de forma segura antes de desconectar.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pdf-to-kindle",
        description="Convierte PDFs y DOCX para leer en Kindle 6\" (11ª generación).",
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Archivos PDF o DOCX a convertir.",
    )
    parser.add_argument(
        "-m", "--modo",
        choices=["auto", "texto", "maquetado", "ocr"],
        default="auto",
        help="Modo de conversión (por defecto: auto).",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output"),
        help="Carpeta de salida (por defecto: ./output).",
    )
    parser.add_argument(
        "--landscape",
        action="store_true",
        help="Activar modo paisaje para diapositivas horizontales.",
    )
    parser.add_argument(
        "--ocr-lang",
        default="spa",
        help="Idioma para OCR (por defecto: spa).",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Enviar los archivos convertidos al Kindle por email.",
    )
    parser.add_argument(
        "--usb",
        type=Path,
        metavar="RUTA",
        help="Copiar archivos al Kindle por USB (ej: E:\\documents o /media/kindle/documents).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    need_ocr = args.modo in ("ocr", "auto")
    ensure_dependencies(need_ocr=need_ocr)

    # Validar archivos de entrada
    for f in args.files:
        if not f.exists():
            print(f"✗ Archivo no encontrado: {f}")
            sys.exit(1)
        if f.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"✗ Formato no soportado: {f.suffix} ({f.name})")
            print(f"  Formatos admitidos: {', '.join(SUPPORTED_EXTENSIONS)}")
            sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  pdf-to-kindle — Modo: {args.modo}")
    print(f"  Archivos: {len(args.files)} | Salida: {args.output}")
    print(f"{'='*50}\n")

    results: list[Path] = []

    for file_path in args.files:
        try:
            print(f"▸ Procesando: {file_path.name}")
            output = process_file(
                input_path=file_path,
                output_dir=args.output,
                mode=args.modo,
                landscape=args.landscape,
                ocr_language=args.ocr_lang,
            )
            results.append(output)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    if not results:
        print("\n⚠  No se generó ningún archivo.")
        sys.exit(1)

    print(f"\n✓ {len(results)} archivo(s) generado(s) en {args.output}/")
    for r in results:
        print(f"  • {r.name}")

    if args.usb:
        try:
            copy_to_kindle_usb(results, args.usb)
        except Exception as e:
            print(f"\n✗ Error al copiar por USB: {e}")
            sys.exit(1)

    if args.send:
        try:
            send_to_kindle(results)
        except Exception as e:
            print(f"\n✗ Error al enviar: {e}")
            sys.exit(1)
