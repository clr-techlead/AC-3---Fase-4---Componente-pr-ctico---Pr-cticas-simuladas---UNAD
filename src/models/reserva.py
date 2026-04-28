# ==============================================================
# reserva.py
# Núcleo del sistema: gestiona el ciclo de vida de una reserva
# Estados: PENDIENTE → CONFIRMADA → CANCELADA
# ==============================================================

import uuid
from datetime import datetime
from typing import Optional
from src.models.cliente import Cliente
from src.models.servicio import Servicio
from src.exceptions.custom_exceptions import (
    ReservaInvalidaError, EstadoReservaError, CalculoCostoError, ValorNegativoError
)
from src.utils.logger import log


class EstadoReserva:
    """Constantes de estado para evitar strings sueltos en el código."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"


class Reserva:
    """
    Representa una reserva de servicio asociada a un cliente.

    Ciclo de vida:
        creación → PENDIENTE → confirmar() → CONFIRMADA
                             → cancelar()  → CANCELADA

    El cálculo del costo se delega al objeto Servicio (polimorfismo),
    garantizando que cada tipo de servicio aplique su propia lógica.
    """

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        cantidad: float,
        nota: str = "",
        descuento: float = 0.0
    ):
        self._validar_creacion(cliente, servicio, cantidad, descuento)

        self.__id: str = str(uuid.uuid4())[:10].upper()
        self.__cliente: Cliente = cliente
        self.__servicio: Servicio = servicio
        self.__cantidad: float = float(cantidad)
        self.__nota: str = nota.strip()
        self.__descuento: float = float(descuento)
        self.__estado: str = EstadoReserva.PENDIENTE
        self.__fecha_creacion: datetime = datetime.now()
        self.__fecha_confirmacion: Optional[datetime] = None
        self.__fecha_cancelacion: Optional[datetime] = None

        # Calcular y almacenar el costo en el momento de la creación
        self.__costo_calculado: float = self._calcular_costo_interno()

        log.info(
            f"Reserva creada: [{self.__id}] | Cliente: {cliente.nombre} | "
            f"Servicio: {servicio.nombre} | Costo: ${self.__costo_calculado:,.2f}"
        )

    # ── Validación inicial ─────────────────────────────────────
    @staticmethod
    def _validar_creacion(
        cliente: Cliente,
        servicio: Servicio,
        cantidad: float,
        descuento: float
    ) -> None:
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("el cliente proporcionado no es válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("el servicio proporcionado no es válido")
        if not servicio.activo:
            raise ReservaInvalidaError(f"el servicio '{servicio.nombre}' está desactivado")
        if cantidad <= 0:
            raise ValorNegativoError("cantidad", cantidad)
        if not (0.0 <= descuento <= 1.0):
            raise ValorNegativoError("descuento", descuento)

    # ── Cálculo de costo ───────────────────────────────────────
    def _calcular_costo_interno(self) -> float:
        try:
            if self.__descuento > 0:
                return self.__servicio.calcular_costo_con_descuento(
                    self.__cantidad, self.__descuento
                )
            return self.__servicio.calcular_costo_con_iva(self.__cantidad)
        except Exception as exc:
            raise CalculoCostoError(
                f"reserva '{self.__id}'", exc
            ) from exc

    # ── Propiedades (solo lectura) ─────────────────────────────
    @property
    def id(self) -> str:
        return self.__id

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def cantidad(self) -> float:
        return self.__cantidad

    @property
    def costo(self) -> float:
        return self.__costo_calculado

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def descuento(self) -> float:
        return self.__descuento

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @property
    def fecha_confirmacion(self) -> Optional[datetime]:
        return self.__fecha_confirmacion

    @property
    def nota(self) -> str:
        return self.__nota

    # ── Transiciones de estado ────────────────────────────────
    def confirmar(self) -> None:
        """
        Transita de PENDIENTE a CONFIRMADA.
        Lanza EstadoReservaError si el estado actual no lo permite.
        """
        if self.__estado != EstadoReserva.PENDIENTE:
            raise EstadoReservaError(self.__estado, "confirmar")
        self.__estado = EstadoReserva.CONFIRMADA
        self.__fecha_confirmacion = datetime.now()
        log.info(f"Reserva confirmada: [{self.__id}] | {self.__cliente.nombre}")

    def cancelar(self, motivo: str = "sin motivo especificado") -> None:
        """
        Transita a CANCELADA desde cualquier estado activo.
        Una reserva ya cancelada no puede cancelarse de nuevo.
        """
        if self.__estado == EstadoReserva.CANCELADA:
            raise EstadoReservaError(self.__estado, "cancelar")
        self.__estado = EstadoReserva.CANCELADA
        self.__fecha_cancelacion = datetime.now()
        log.warning(
            f"Reserva cancelada: [{self.__id}] | Motivo: {motivo} | "
            f"Cliente: {self.__cliente.nombre}"
        )

    # ── Representación ─────────────────────────────────────────
    def __repr__(self) -> str:
        return (
            f"Reserva(id='{self.__id}', estado='{self.__estado}', "
            f"cliente='{self.__cliente.nombre}', servicio='{self.__servicio.nombre}', "
            f"costo=${self.__costo_calculado:,.2f})"
        )

    def resumen(self) -> dict:
        """Genera un diccionario legible con los datos principales de la reserva."""
        return {
            "id": self.__id,
            "estado": self.__estado,
            "cliente": self.__cliente.nombre,
            "servicio": self.__servicio.nombre,
            "cantidad": self.__cantidad,
            "descuento_pct": f"{self.__descuento * 100:.0f}%",
            "costo_total": f"${self.__costo_calculado:,.2f}",
            "creada": self.__fecha_creacion.strftime("%Y-%m-%d %H:%M"),
            "nota": self.__nota or "—",
        }
