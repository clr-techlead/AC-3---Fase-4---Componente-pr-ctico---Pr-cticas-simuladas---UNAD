# ==============================================================
# cliente.py
# Modelo Cliente - Sistema Software FJ
# Implementa encapsulación, validaciones y manejo de errores
# ==============================================================

import re
import uuid

from src.exceptions.custom_exceptions import (
    ClienteInvalidoError,
    CampoVacioError
)

from src.utils.logger import log


class Cliente:
    """
    Representa un cliente dentro del sistema.

    Implementa:
    - Encapsulación
    - Validaciones robustas
    - Manejo de excepciones
    - Serialización
    """

    # ----------------------------------------------------------
    # Expresiones regulares
    # ----------------------------------------------------------

    _REGEX_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")
    _REGEX_TELEFONO = re.compile(r"^\+?[0-9]{7,15}$")

    # ----------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------

    def __init__(self, nombre: str, email: str, telefono: str):

        try:

            self.__id = str(uuid.uuid4())[:8].upper()

            self.nombre = nombre
            self.email = email
            self.telefono = telefono

            log.info(
                f"Cliente creado correctamente: "
                f"{self.__id} - {self.__nombre}"
            )

        except Exception as e:

            log.error(f"Error creando cliente: {e}")

            raise ClienteInvalidoError(
                "datos del cliente",
                str(e)
            ) from e

    # ----------------------------------------------------------
    # ID (solo lectura)
    # ----------------------------------------------------------

    @property
    def id(self) -> str:
        return self.__id

    # ----------------------------------------------------------
    # Nombre
    # ----------------------------------------------------------

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):

        if not isinstance(valor, str) or not valor.strip():
            raise CampoVacioError("nombre")

        valor = valor.strip()

        if len(valor) < 2:
            raise ClienteInvalidoError("nombre", valor)

        self.__nombre = valor.title()

    # ----------------------------------------------------------
    # Email
    # ----------------------------------------------------------

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):

        if not isinstance(valor, str) or not valor.strip():
            raise CampoVacioError("email")

        valor = valor.strip().lower()

        if not self._REGEX_EMAIL.match(valor):
            raise ClienteInvalidoError("email", valor)

        self.__email = valor

    # ----------------------------------------------------------
    # Teléfono
    # ----------------------------------------------------------

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):

        if not isinstance(valor, str) or not valor.strip():
            raise CampoVacioError("telefono")

        valor = valor.strip()

        if not self._REGEX_TELEFONO.match(valor):
            raise ClienteInvalidoError("telefono", valor)

        self.__telefono = valor

    # ----------------------------------------------------------
    # Métodos auxiliares
    # ----------------------------------------------------------

    def actualizar_datos(
        self,
        nombre=None,
        email=None,
        telefono=None
    ):
        """
        Actualiza parcialmente los datos del cliente.
        """

        try:

            if nombre is not None:
                self.nombre = nombre

            if email is not None:
                self.email = email

            if telefono is not None:
                self.telefono = telefono

            log.info(f"Cliente actualizado: {self.__id}")

        except Exception as e:

            log.error(f"Error actualizando cliente: {e}")

            raise

    def mostrar_info(self):
        """
        Retorna una representación amigable del cliente.
        """

        return (
            f"Cliente: {self.__nombre}\n"
            f"Correo: {self.__email}\n"
            f"Teléfono: {self.__telefono}"
        )

    # ----------------------------------------------------------
    # Serialización
    # ----------------------------------------------------------

    def to_dict(self) -> dict:

        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "email": self.__email,
            "telefono": self.__telefono
        }

    # ----------------------------------------------------------
    # Métodos especiales
    # ----------------------------------------------------------

    def __repr__(self):

        return (
            f"Cliente("
            f"id='{self.__id}', "
            f"nombre='{self.__nombre}', "
            f"email='{self.__email}', "
            f"telefono='{self.__telefono}')"
        )

    def __str__(self):

        return (
            f"{self.__nombre} "
            f"({self.__email})"
        )

    def __eq__(self, otro):

        if not isinstance(otro, Cliente):
            return False

        return self.__id == otro.__id
