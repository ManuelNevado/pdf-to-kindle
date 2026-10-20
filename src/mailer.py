"""Envío de archivos convertidos a Kindle por SMTP."""

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
import os


def load_smtp_config() -> dict[str, str]:
    load_dotenv()
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "KINDLE_EMAIL"]
    config = {}
    missing = []
    for key in required:
        val = os.getenv(key)
        if not val:
            missing.append(key)
        else:
            config[key] = val
    if missing:
        raise RuntimeError(
            f"Faltan variables en .env: {', '.join(missing)}\n"
            f"Copia .env.example a .env y completa los valores."
        )
    return config


def send_to_kindle(files: list[Path]) -> None:
    config = load_smtp_config()

    msg = MIMEMultipart()
    msg["From"] = config["SMTP_USER"]
    msg["To"] = config["KINDLE_EMAIL"]
    msg["Subject"] = "Documento para Kindle"
    msg.attach(MIMEText("Enviado con pdf-to-kindle.", "plain"))

    for file_path in files:
        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename={file_path.name}"
        )
        msg.attach(part)

    print(f"\n📧 Enviando {len(files)} archivo(s) a {config['KINDLE_EMAIL']}...")
    with smtplib.SMTP(config["SMTP_HOST"], int(config["SMTP_PORT"])) as server:
        server.starttls()
        server.login(config["SMTP_USER"], config["SMTP_PASSWORD"])
        server.send_message(msg)
    print("  ✓ Enviado correctamente.")
