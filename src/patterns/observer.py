# ==============================================================
# observer.py
# Patrón Observer — notificaciones automáticas ante eventos
# Desacopla la lógica de negocio de los efectos secundarios
# ==============================================================

from abc import ABC, abstractmethod
from typing import List
from src.utils.logger import log


# ─────────────────────────────────────────────────────────────
# INTERFAZ DEL OBSERVADOR
# ─────────────────────────────────────────────────────────────

class Observador(ABC):
    """
    Contrato que debe cumplir cualquier componente que quiera
    recibir notificaciones de cambios en el sistema.
    """

    @abstractmethod
    def actualizar(self, evento: str, datos: dict) -> None:
        """
        Se invoca cada vez que el sujeto emite un evento.

        evento : nombre del evento (ej: "reserva_confirmada")
        datos  : diccionario con información relevante del evento
        """
        ...


# ─────────────────────────────────────────────────────────────
# SUJETO OBSERVABLE (mixin)
# ─────────────────────────────────────────────────────────────

class Observable:
    """
    Mixin que dota de capacidad de notificación a cualquier clase.
    Se diseñó como mixin para no forzar una herencia rígida.
    """

    def __init__(self):
        self._observadores: List[Observador] = []

    def suscribir(self, observador: Observador) -> None:
        """Registra un observador. Ignora duplicados."""
        if observador not in self._observadores:
            self._observadores.append(observador)
            log.debug(f"Observer suscrito: {observador.__class__.__name__}")

    def desuscribir(self, observador: Observador) -> None:
        """Elimina un observador de la lista."""
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, evento: str, datos: dict) -> None:
        """
        Recorre todos los observadores registrados y les envía el evento.
        Los errores individuales de cada observador no interrumpen la cadena.
        """
        for obs in self._observadores:
            try:
                obs.actualizar(evento, datos)
            except Exception as exc:
                log.error(
                    f"Error en observador {obs.__class__.__name__} "
                    f"para evento '{evento}': {exc}"
                )


# ─────────────────────────────────────────────────────────────
# IMPLEMENTACIONES CONCRETAS DE OBSERVADORES
# ─────────────────────────────────────────────────────────────

class NotificadorCorreo(Observador):
    """
    Simula el envío de un correo electrónico ante eventos clave.
    En producción real, aquí iría la integración con un servicio SMTP.
    """

    EVENTOS_DE_INTERES = {
        "reserva_confirmada",
        "reserva_cancelada",
        "reserva_creada",
    }

    def actualizar(self, evento: str, datos: dict) -> None:
        if evento not in self.EVENTOS_DE_INTERES:
            return
        destinatario = datos.get("email", "sin-email")
        cliente = datos.get("cliente", "Cliente")
        mensaje = self._construir_mensaje(evento, cliente, datos)
        log.info(f"[CORREO] Para: {destinatario} | Asunto: {evento} | {mensaje}")
        print(f"  📧 Correo simulado → {destinatario}: {mensaje}")

    @staticmethod
    def _construir_mensaje(evento: str, cliente: str, datos: dict) -> str:
        servicio = datos.get("servicio", "servicio")
        costo = datos.get("costo", "N/A")
        mensajes = {
            "reserva_creada":     f"Hola {cliente}, tu reserva de '{servicio}' fue recibida.",
            "reserva_confirmada": f"Hola {cliente}, tu reserva de '{servicio}' está CONFIRMADA. Total: {costo}",
            "reserva_cancelada":  f"Hola {cliente}, tu reserva de '{servicio}' fue CANCELADA.",
        }
        return mensajes.get(evento, f"Evento: {evento}")


class NotificadorFacturacion(Observador):
    """
    Observa confirmaciones de reserva para registrarlas
    en el módulo de facturación (registro en log por ahora).
    """

    def actualizar(self, evento: str, datos: dict) -> None:
        if evento != "reserva_confirmada":
            return
        reserva_id = datos.get("reserva_id", "?")
        costo = datos.get("costo", 0)
        log.info(
            f"[FACTURACIÓN] Reserva {reserva_id} confirmada. "
            f"Monto a facturar: {costo}"
        )


class RegistroAuditoria(Observador):
    """
    Registra todos los eventos del sistema para fines de auditoría.
    No filtra por tipo de evento: lo guarda todo.
    """

    def __init__(self):
        self._historial: list = []

    def actualizar(self, evento: str, datos: dict) -> None:
        from datetime import datetime
        entrada = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "evento": evento,
            "datos": datos,
        }
        self._historial.append(entrada)
        log.debug(f"[AUDITORÍA] {evento} registrado. Total entradas: {len(self._historial)}")

    def obtener_historial(self) -> list:
        return list(self._historial)
