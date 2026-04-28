# ==============================================================
# logger.py
# Módulo de logging centralizado para Software FJ
# Registra eventos y errores en logs/app.log
# ==============================================================

import logging
import os
from datetime import datetime


def _construir_ruta_log() -> str:
    """
    Calcula la ruta absoluta a logs/app.log sin importar desde dónde
    se ejecute el programa. Crea el directorio si no existe.
    """
    raiz_proyecto = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    directorio_logs = os.path.join(raiz_proyecto, "logs")
    os.makedirs(directorio_logs, exist_ok=True)
    return os.path.join(directorio_logs, "app.log")


def obtener_logger(nombre: str = "software_fj") -> logging.Logger:
    """
    Devuelve un logger ya configurado con dos handlers:
      - FileHandler  → escribe en logs/app.log
      - StreamHandler → imprime en consola (nivel WARNING o superior)

    Si el logger con ese nombre ya fue configurado anteriormente,
    lo devuelve directamente para evitar duplicar handlers.
    """
    logger = logging.getLogger(nombre)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # --- Handler de archivo (todos los niveles) ---
    ruta_log = _construir_ruta_log()
    handler_archivo = logging.FileHandler(ruta_log, encoding="utf-8")
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)

    # --- Handler de consola (solo WARNING en adelante) ---
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.WARNING)
    handler_consola.setFormatter(formato)

    logger.addHandler(handler_archivo)
    logger.addHandler(handler_consola)

    logger.info(f"Logger '{nombre}' inicializado. Archivo: {ruta_log}")
    return logger


# Instancia global lista para importar directamente
log = obtener_logger()
