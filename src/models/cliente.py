# ==============================================================
# cliente.py
# Modelo de dominio: Cliente del sistema Software FJ
# Aplica encapsulación fuerte y validación en los setters
# ==============================================================

import re
import uuid
from src.exceptions.custom_exceptions import (
    ClienteInvalidoError, CampoVacioError, ValorNegativoError
)
from src.utils.logger import log


class Cliente:
    """
    Representa a un cliente registrado en el sistema.

    Atributos privados con getters y setters que validan
    cada dato antes de asignarlo, garantizando integridad
    desde el momento de la creación.
    """

    _REGEX_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")
    _REGEX_TELEFONO = re.compile(r"^\+?[0-9]{7,15}$")

    def __init__(self, nombre: str, email: str, telefono: str):
        # Se usa un ID único auto-generado para evitar colisiones
        self.__id: str = str(uuid.uuid4())[:8].upper()
        self.nombre = nombre       # Pasa por el setter
        self.email = email
        self.telefono = telefono
        log.info(f"Cliente creado: {self.__id} | {self.__nombre}")

    # ── ID (solo lectura) ──────────────────────────────────────
    @property
    def id(self) -> str:
        return self.__id

    # ── Nombre ────────────────────────────────────────────────
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise CampoVacioError("nombre")
        if len(valor.strip()) < 2:
            raise ClienteInvalidoError("nombre", valor)
        self.__nombre = valor.strip().title()

    # ── Email ─────────────────────────────────────────────────
    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise CampoVacioError("email")
        if not self._REGEX_EMAIL.match(valor.strip().lower()):
            raise ClienteInvalidoError("email", valor)
        self.__email = valor.strip().lower()

    # ── Teléfono ──────────────────────────────────────────────
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise CampoVacioError("telefono")
        if not self._REGEX_TELEFONO.match(valor.strip()):
            raise ClienteInvalidoError("telefono", valor)
        self.__telefono = valor.strip()

    # ── Representación ────────────────────────────────────────
    def __repr__(self) -> str:
        return (
            f"Cliente(id='{self.__id}', nombre='{self.__nombre}', "
            f"email='{self.__email}', telefono='{self.__telefono}')"
        )

    def __eq__(self, otro) -> bool:
        if not isinstance(otro, Cliente):
            return False
        return self.__id == otro.__id

    def to_dict(self) -> dict:
        """Serializa el cliente a diccionario (útil para logs y reportes)."""
        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "email": self.__email,
            "telefono": self.__telefono,
        }
