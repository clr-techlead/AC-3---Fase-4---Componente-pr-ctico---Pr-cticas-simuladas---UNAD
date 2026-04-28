# ==============================================================
# factura.py
# Modelo de Factura — se genera al confirmar una reserva
# Número correlativo, detalle completo, subtotal, IVA y total
# ==============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.reserva import Reserva

from src.utils.logger import log


class _ContadorFacturas:
    """Contador interno que genera números de factura correlativos."""
    _siguiente: int = 1

    @classmethod
    def siguiente(cls) -> int:
        numero = cls._siguiente
        cls._siguiente += 1
        return numero

    @classmethod
    def reiniciar(cls) -> None:
        """Útil para tests — permite resetear el contador."""
        cls._siguiente = 1


@dataclass
class LineaFactura:
    """Representa una línea de detalle dentro de la factura."""
    descripcion: str
    cantidad: float
    precio_unitario: float
    descuento_pct: float = 0.0

    @property
    def subtotal_linea(self) -> float:
        return round(self.cantidad * self.precio_unitario * (1 - self.descuento_pct), 2)

    def __str__(self) -> str:
        desc_txt = f" (-{self.descuento_pct:.0%})" if self.descuento_pct > 0 else ""
        return (
            f"  {self.descripcion:<35} x{self.cantidad:<6.1f} "
            f"@ ${self.precio_unitario:>10,.0f}{desc_txt} = ${self.subtotal_linea:>12,.2f}"
        )


class Factura:
    """
    Representa el documento fiscal generado al confirmar una reserva.

    Responsabilidades:
    - Asignar número único correlativo
    - Calcular subtotal, IVA y total final
    - Generar representación imprimible
    - Exportar a diccionario para reportes
    """

    IVA: float = 0.19

    def __init__(self, reserva):
        self.__numero: int = _ContadorFacturas.siguiente()
        self.__fecha: datetime = datetime.now()
        self.__reserva = reserva
        self.__lineas = []
        self._construir_lineas()
        log.info(
            f"Factura #{self.__numero:04d} generada | "
            f"Reserva: {reserva.id} | Total: ${self.total:,.2f}"
        )

    def _construir_lineas(self) -> None:
        """Genera las líneas de detalle a partir de la reserva."""
        reserva = self.__reserva
        linea = LineaFactura(
            descripcion=reserva.servicio.descripcion(),
            cantidad=reserva.cantidad,
            precio_unitario=reserva.servicio.precio_base,
            descuento_pct=reserva.descuento,
        )
        self.__lineas.append(linea)

    @property
    def numero(self) -> str:
        return f"FJ-{self.__numero:04d}"

    @property
    def fecha(self) -> datetime:
        return self.__fecha

    @property
    def subtotal(self) -> float:
        return round(sum(l.subtotal_linea for l in self.__lineas), 2)

    @property
    def iva_valor(self) -> float:
        return round(self.subtotal * self.IVA, 2)

    @property
    def total(self) -> float:
        return round(self.subtotal + self.iva_valor, 2)

    def imprimir(self) -> str:
        """Devuelve la factura formateada como string imprimible."""
        sep = "=" * 65
        reserva = self.__reserva
        lineas = [
            sep,
            "  FACTURA DE SERVICIOS — Software FJ",
            f"  Número   : {self.numero}",
            f"  Fecha    : {self.__fecha.strftime('%Y-%m-%d %H:%M')}",
            f"  Cliente  : {reserva.cliente.nombre}",
            f"  Email    : {reserva.cliente.email}",
            sep,
            "  DETALLE DE SERVICIOS",
            "─" * 65,
        ]
        for linea in self.__lineas:
            lineas.append(str(linea))
        lineas += [
            "─" * 65,
            f"  {'Subtotal':<40} ${self.subtotal:>18,.2f}",
            f"  {'IVA (19%)':<40} ${self.iva_valor:>18,.2f}",
            sep,
            f"  {'TOTAL A PAGAR':<40} ${self.total:>18,.2f}",
            sep,
            f"  Reserva ref.: {reserva.id}  |  Estado: {reserva.estado}",
            sep,
        ]
        return "\n".join(lineas)

    def to_dict(self) -> dict:
        """Serializa la factura a diccionario para exportación o log."""
        return {
            "numero": self.numero,
            "fecha": self.__fecha.strftime("%Y-%m-%d %H:%M"),
            "cliente": self.__reserva.cliente.nombre,
            "email": self.__reserva.cliente.email,
            "reserva_id": self.__reserva.id,
            "servicio": self.__reserva.servicio.nombre,
            "subtotal": self.subtotal,
            "iva": self.iva_valor,
            "total": self.total,
        }

    def __repr__(self) -> str:
        return f"Factura(numero='{self.numero}', total=${self.total:,.2f})"
