# ==============================================================
# strategy.py
# Patrón Strategy — algoritmos intercambiables de descuento
# Cada estrategia encapsula una política de precio diferente
# ==============================================================

from abc import ABC, abstractmethod
from src.utils.logger import log


# ─────────────────────────────────────────────────────────────
# INTERFAZ DE ESTRATEGIA
# ─────────────────────────────────────────────────────────────

class EstrategiaDescuento(ABC):
    """
    Define el contrato que deben cumplir todas las estrategias
    de descuento. Recibe el precio bruto y devuelve el factor
    de descuento a aplicar (valor entre 0.0 y 1.0).
    """

    @abstractmethod
    def calcular_factor(self, precio_base: float, cantidad: float) -> float:
        """
        Devuelve el factor de descuento (0.0 = sin descuento, 0.3 = 30%).
        El precio final se calcula como: precio_base * (1 - factor).
        """
        ...

    @abstractmethod
    def descripcion(self) -> str:
        """Devuelve una descripción legible de la estrategia."""
        ...

    def aplicar(self, precio_bruto: float, cantidad: float) -> float:
        """
        Método plantilla: obtiene el factor y lo aplica sobre el precio.
        Los subclases solo necesitan implementar calcular_factor().
        """
        factor = self.calcular_factor(precio_bruto, cantidad)
        precio_final = round(precio_bruto * (1 - factor), 2)
        log.debug(
            f"Estrategia '{self.descripcion()}': "
            f"bruto={precio_bruto:.2f}, factor={factor:.2%}, final={precio_final:.2f}"
        )
        return precio_final


# ─────────────────────────────────────────────────────────────
# ESTRATEGIAS CONCRETAS
# ─────────────────────────────────────────────────────────────

class SinDescuento(EstrategiaDescuento):
    """Precio estándar sin ningún tipo de reducción."""

    def calcular_factor(self, precio_base: float, cantidad: float) -> float:
        return 0.0

    def descripcion(self) -> str:
        return "Precio estándar (sin descuento)"


class DescuentoClienteVIP(EstrategiaDescuento):
    """
    Descuento fijo del 20% para clientes catalogados como VIP.
    Se aplica independientemente de la cantidad reservada.
    """

    DESCUENTO_VIP: float = 0.20

    def calcular_factor(self, precio_base: float, cantidad: float) -> float:
        return self.DESCUENTO_VIP

    def descripcion(self) -> str:
        return f"Cliente VIP ({self.DESCUENTO_VIP:.0%} de descuento)"


class DescuentoVolumen(EstrategiaDescuento):
    """
    Descuento escalonado según la cantidad de unidades reservadas.
    < 5  unidades → 0%
    5-9  unidades → 10%
    ≥ 10 unidades → 20%
    """

    def calcular_factor(self, precio_base: float, cantidad: float) -> float:
        if cantidad >= 10:
            return 0.20
        elif cantidad >= 5:
            return 0.10
        return 0.0

    def descripcion(self) -> str:
        return "Descuento por volumen (escalonado 10% / 20%)"


class DescuentoTemporadaBaja(EstrategiaDescuento):
    """
    Descuento del 15% aplicado durante temporada baja.
    Se activa entre los meses de enero y marzo.
    """

    DESCUENTO_TEMPORADA: float = 0.15
    MESES_TEMPORADA_BAJA: tuple = (1, 2, 3)

    def calcular_factor(self, precio_base: float, cantidad: float) -> float:
        from datetime import date
        mes_actual = date.today().month
        if mes_actual in self.MESES_TEMPORADA_BAJA:
            return self.DESCUENTO_TEMPORADA
        return 0.0

    def descripcion(self) -> str:
        return f"Temporada baja ({self.DESCUENTO_TEMPORADA:.0%} ene-mar)"


class DescuentoCombinado(EstrategiaDescuento):
    """
    Combina dos estrategias: aplica primero la de mayor factor.
    Permite componer políticas sin modificar las clases existentes.
    """

    def __init__(self, estrategia_a: EstrategiaDescuento, estrategia_b: EstrategiaDescuento):
        self._a = estrategia_a
        self._b = estrategia_b

    def calcular_factor(self, precio_base: float, cantidad: float) -> float:
        fa = self._a.calcular_factor(precio_base, cantidad)
        fb = self._b.calcular_factor(precio_base, cantidad)
        # Se aplica el mayor de los dos descuentos (no se suman para evitar abuso)
        return max(fa, fb)

    def descripcion(self) -> str:
        return f"Combinado: [{self._a.descripcion()}] + [{self._b.descripcion()}]"
