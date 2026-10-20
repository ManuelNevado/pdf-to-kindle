# pdf-to-kindle

Herramienta en Python para convertir PDFs (y DOCX) y optimizarlos para lectura en un **Kindle de 6"** (11ª generación).

## Características

- **Modo texto**: convierte a EPUB con `ebook-convert` (Calibre). Ideal para documentos de texto puro.
- **Modo maquetado**: optimiza con `k2pdfopt` para PDFs con tablas, figuras o columnas. Recorta márgenes automáticamente.
- **Modo OCR**: detecta PDFs escaneados y aplica OCR con `OCRmyPDF` (español por defecto) antes de convertir.
- **Modo auto**: analiza cada archivo y elige automáticamente el mejor modo de conversión.
- **Soporte DOCX**: acepta archivos `.docx` además de `.pdf`.
- **Páginas horizontales**: detecta y maneja diapositivas en formato paisaje (rotar/dividir).
- **Envío a Kindle**: envía los archivos convertidos por email a tu dirección `@kindle.com` vía SMTP.

## Requisitos

### Python 3.10+

```bash
pip install -r requirements.txt
```

### Dependencias externas

| Herramienta | Para qué se usa | Instalación |
|---|---|---|
| **Calibre** (`ebook-convert`) | Conversión a EPUB | [calibre-ebook.com/download](https://calibre-ebook.com/download) |
| **k2pdfopt** | Optimización de maquetado | [willus.com/k2pdfopt](https://www.willus.com/k2pdfopt/) |
| **OCRmyPDF** + **Tesseract** | OCR de PDFs escaneados | `pip install ocrmypdf` + [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) |

> La app comprueba al inicio si las herramientas necesarias están instaladas y te indica cómo instalarlas si falta alguna.

#### Tesseract (idioma español)

```bash
# Windows: descargar desde https://github.com/UB-Mannheim/tesseract/wiki
# y seleccionar el paquete de idioma español durante la instalación.

# Linux
sudo apt install tesseract-ocr tesseract-ocr-spa

# macOS
brew install tesseract tesseract-lang
```

## Uso

```bash
# Modo automático (detecta el tipo de PDF)
python main.py documento.pdf

# Varios archivos
python main.py apuntes.pdf tfm.pdf presentacion.pdf

# Modo texto (forzar EPUB)
python main.py -m texto apuntes.pdf

# Modo maquetado (PDFs con tablas/figuras)
python main.py -m maquetado paper.pdf

# Modo OCR (PDF escaneado)
python main.py -m ocr escaneo.pdf

# Activar modo paisaje para diapositivas
python main.py --landscape presentacion.pdf

# Convertir un DOCX
python main.py apuntes.docx

# Carpeta de salida personalizada
python main.py -o kindle_files documento.pdf

# Convertir y enviar al Kindle
python main.py --send documento.pdf
```

### Opciones

| Opción | Descripción |
|---|---|
| `-m, --modo` | `auto`, `texto`, `maquetado`, `ocr` (por defecto: `auto`) |
| `-o, --output` | Carpeta de salida (por defecto: `./output`) |
| `--landscape` | Activar modo paisaje para diapositivas horizontales |
| `--ocr-lang` | Idioma OCR (por defecto: `spa`) |
| `--send` | Enviar los archivos convertidos al Kindle por email |

## Configuración del envío por email

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Completa los datos en `.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=tu_correo@gmail.com
   SMTP_PASSWORD=tu_contraseña_de_aplicacion
   KINDLE_EMAIL=tu_usuario@kindle.com
   ```

3. Si usas Gmail, necesitas una [contraseña de aplicación](https://myaccount.google.com/apppasswords).

4. Añade tu correo a la lista de remitentes aprobados en la configuración de tu Kindle (Amazon → Manage Your Content and Devices → Preferences → Personal Document Settings).

## Estructura del proyecto

```
pdf-to-kindle/
├── main.py              # Punto de entrada
├── src/
│   ├── cli.py           # Interfaz de línea de comandos
│   ├── config.py        # Verificación de dependencias
│   ├── converter.py     # Lógica de conversión
│   ├── detector.py      # Análisis de PDFs
│   └── mailer.py        # Envío por email
├── requirements.txt
├── .env.example
└── README.md
```
