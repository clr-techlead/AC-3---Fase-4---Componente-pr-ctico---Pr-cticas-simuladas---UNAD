# ==============================================================
# servicio.py
# Jerarquía de servicios: clase abstracta + 3 implementaciones
# Demuestra: Abstracción, Herencia y Polimorfismo
# ==============================================================

from abc import ABC, abstractmethod
import uuid
from src.exceptions.custom_exceptions import (
    ValorNegativoError, CampoVacioError, CalculoCostoError
)
from src.utils.logger import log


# ─────────────────────────────────────────────────────────────
# CLASE ABSTRACTA BASE
# ─────────────────────────────────────────────────────────────

class Servicio(ABC):
    """
    Contrato común para todos los servicios que ofrece Software FJ.
    Ninguna instancia directa es posible; solo las subclases concretas.
    """

    IMPUESTO_IVA: float = 0.19  # 19 % IVA Colombia

    def __init__(self, nombre: str, precio_base: float):
        if not nombre or not nombre.strip():
            raise CampoVacioError("nombre del servicio")
        if precio_base < 0:
            raise ValorNegativoError("precio_base", precio_base)

        self.__id: str = str(uuid.uuid4())[:8].upper()
        self.__nombre: str = nombre.strip()
        self.__precio_base: float = float(precio_base)
        self.__activo: bool = True
        log.info(f"Servicio registrado: [{self.__id}] {self.__nombre} - ${self.__precio_base:,.0f}")

    # ── Getters básicos ────────────────────────────────────────
    @property
    def id(self) -> str:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def precio_base(self) -> float:
        return self.__precio_base

    @property
    def activo(self) -> bool:
        return self.__activo

    def desactivar(self) -> None:
        self.__activo = False
        log.warning(f"Servicio desactivado: {self.__id} | {self.__nombre}")

    # ── Métodos abstractos (contrato) ─────────────────────────
    @abstractmethod
    def calcular_costo(self, cantidad: float) -> float:
        """Calcula el costo sin impuestos según las reglas del servicio."""
        ...

    @abstractmethod
    def descripcion(self) -> str:
        """Devuelve una descripción legible del servicio."""
        ...

    # ── Costo con impuesto (polimorfismo de comportamiento) ────
    def calcular_costo_con_iva(self, cantidad: float) -> float:
        """Aplica IVA sobre el resultado de calcular_costo()."""
        try:
            subtotal = self.calcular_costo(cantidad)
            total = subtotal * (1 + self.IMPUESTO_IVA)
            log.debug(f"Costo con IVA ({self.nombre}): subtotal={subtotal:.2f} total={total:.2f}")
            return round(total, 2)
        except Exception as exc:
            raise CalculoCostoError(f"calcular_costo_con_iva en '{self.nombre}'", exc) from exc

    def calcular_costo_con_descuento(self, cantidad: float, descuento: float) -> float:
        """
        Aplica un descuento porcentual antes de calcular IVA.
        descuento: valor entre 0.0 y 1.0 (p.ej. 0.10 = 10 %).
        """
        if not (0 <= descuento <= 1):
            raise ValorNegativoError("descuento", descuento)
        try:
            subtotal = self.calcular_costo(cantidad)
            con_descuento = subtotal * (1 - descuento)
            total = con_descuento * (1 + self.IMPUESTO_IVA)
            log.debug(
                f"Costo con descuento {descuento*100:.0f}% e IVA ({self.nombre}): "
                f"subtotal={subtotal:.2f} neto={con_descuento:.2f} total={total:.2f}"
            )
            return round(total, 2)
        except CalculoCostoError:
            raise
        except Exception as exc:
            raise CalculoCostoError(f"calcular_costo_con_descuento en '{self.nombre}'", exc) from exc

    def __repr__(self) -> str:
        estado = "activo" if self.__activo else "inactivo"
        return f"{self.__class__.__name__}(id='{self.__id}', nombre='{self.__nombre}', estado={estado})"


# ─────────────────────────────────────────────────────────────
# SUBCLASE 1: ReservaSala
# ─────────────────────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión o conferencia.
    El costo se calcula por hora de uso.
    """

    def __init__(self, nombre: str, precio_por_hora: float, capacidad: int):
        super().__init__(nombre, precio_por_hora)
        if capacidad <= 0:
            raise ValorNegativoError("capacidad", capacidad)
        self.__capacidad = int(capacidad)

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    def calcular_costo(self, horas: float) -> float:
        """horas: duración de la reserva en horas (mínimo 0.5)."""
        if horas <= 0:
            raise ValorNegativoError("horas", horas)
        horas_efectivas = max(horas, 0.5)
        return round(self.precio_base * horas_efectivas, 2)

    def descripcion(self) -> str:
        return (
            f"Sala '{self.nombre}' — capacidad {self.__capacidad} personas, "
            f"${self.precio_base:,.0f}/hora"
        )


# ─────────────────────────────────────────────────────────────
# SUBCLASE 2: AlquilerEquipo
# ─────────────────────────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (proyectores, laptops, etc.).
    El costo se calcula por día de alquiler con recargo por fin de semana.
    """

    _RECARGO_FIN_SEMANA: float = 0.15  # 15 % adicional

    def __init__(self, nombre: str, precio_por_dia: float, incluye_seguro: bool = False):
        super().__init__(nombre, precio_por_dia)
        self.__incluye_seguro = incluye_seguro
        self.__costo_seguro = precio_por_dia * 0.05 if incluye_seguro else 0.0

    @property
    def incluye_seguro(self) -> bool:
        return self.__incluye_seguro

    def calcular_costo(self, dias: float, dias_fin_semana: int = 0) -> float:
        """
        dias: total de días de alquiler.
        dias_fin_semana: cuántos de esos días son sábado/domingo.
        """
        if dias <= 0:
            raise ValorNegativoError("dias", dias)
        if dias_fin_semana < 0 or dias_fin_semana > dias:
            raise ValorNegativoError("dias_fin_semana", dias_fin_semana)

        costo_base = self.precio_base * dias
        recargo = self.precio_base * dias_fin_semana * self._RECARGO_FIN_SEMANA
        seguro = self.__costo_seguro * dias
        return round(costo_base + recargo + seguro, 2)

    def descripcion(self) -> str:
        seguro_txt = "con seguro" if self.__incluye_seguro else "sin seguro"
        return (
            f"Equipo '{self.nombre}' — ${self.precio_base:,.0f}/día, {seguro_txt}"
        )


# ─────────────────────────────────────────────────────────────
# SUBCLASE 3: Asesoria
# ─────────────────────────────────────────────────────────────

class Asesoria(Servicio):
    """
    Servicio de asesoría profesional (técnica, legal, financiera).
    El costo se calcula por sesión con tarifa diferencial según nivel.
    """

    NIVELES_VALIDOS = ("junior", "senior", "experto")

    def __init__(self, nombre: str, tarifa_hora: float, nivel: str = "senior"):
        super().__init__(nombre, tarifa_hora)
        nivel_normalizado = nivel.strip().lower()
        if nivel_normalizado not in self.NIVELES_VALIDOS:
            from src.exceptions.custom_exceptions import ClienteInvalidoError
            raise ClienteInvalidoError("nivel de asesoría", nivel)
        self.__nivel = nivel_normalizado
        self.__multiplicadores = {"junior": 1.0, "senior": 1.35, "experto": 1.75}

    @property
    def nivel(self) -> str:
        return self.__nivel

    def calcular_costo(self, horas: float) -> float:
        """horas: duración de la sesión de asesoría."""
        if horas <= 0:
            raise ValorNegativoError("horas de asesoría", horas)
        multiplicador = self.__multiplicadores[self.__nivel]
        return round(self.precio_base * horas * multiplicador, 2)

    def descripcion(self) -> str:
        return (
            f"Asesoría '{self.nombre}' — nivel {self.__nivel.capitalize()}, "
            f"${self.precio_base:,.0f}/hora base"
        )
