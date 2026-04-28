# ==============================================================
# gestion_reservas.py
# Capa de servicio: orquesta clientes, servicios y reservas
# Toda la lógica de negocio y manejo de excepciones vive aquí
# ==============================================================

from typing import List, Optional
from src.models.cliente import Cliente
from src.models.servicio import Servicio
from src.models.reserva import Reserva, EstadoReserva
from src.exceptions.custom_exceptions import (
    ClienteInvalidoError, ServicioNoEncontradoError,
    ReservaInvalidaError, ReservaDuplicadaError,
    EstadoReservaError, CalculoCostoError
)
from src.utils.logger import log


class GestionReservas:
    """
    Fachada principal del sistema Software FJ.

    Administra tres colecciones en memoria:
      - _clientes  : lista de objetos Cliente
      - _servicios : lista de objetos Servicio
      - _reservas  : lista de objetos Reserva

    Cada método público aplica al menos un bloque try/except y
    registra el resultado en el logger, garantizando que ningún
    error detenga la ejecución del sistema.
    """

    def __init__(self):
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        log.info("Sistema Software FJ iniciado correctamente.")

    # ══════════════════════════════════════════════════════════
    # GESTIÓN DE CLIENTES
    # ══════════════════════════════════════════════════════════

    def registrar_cliente(
        self, nombre: str, email: str, telefono: str
    ) -> Optional[Cliente]:
        """
        Crea y registra un nuevo cliente.
        Usa try/except/else para separar el flujo de error del flujo exitoso.
        """
        try:
            # Validar duplicado por email antes de crear
            if self._buscar_cliente_por_email(email):
                raise ClienteInvalidoError(
                    "email", f"{email} ya está registrado"
                )
            cliente = Cliente(nombre, email, telefono)
        except ClienteInvalidoError as exc:
            log.error(f"No se pudo registrar cliente: {exc}")
            return None
        except Exception as exc:
            log.error(f"Error inesperado al registrar cliente: {exc}")
            return None
        else:
            self._clientes.append(cliente)
            log.info(f"Cliente registrado exitosamente: {cliente.id}")
            return cliente

    def obtener_cliente(self, id_cliente: str) -> Optional[Cliente]:
        """Recupera un cliente por ID. Devuelve None si no existe."""
        return next((c for c in self._clientes if c.id == id_cliente), None)

    def listar_clientes(self) -> List[Cliente]:
        return list(self._clientes)

    def _buscar_cliente_por_email(self, email: str) -> Optional[Cliente]:
        return next(
            (c for c in self._clientes if c.email == email.strip().lower()),
            None
        )

    # ══════════════════════════════════════════════════════════
    # GESTIÓN DE SERVICIOS
    # ══════════════════════════════════════════════════════════

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """
        Añade un servicio al catálogo.
        Usa try/except/finally para garantizar el log incluso en error.
        """
        resultado = False
        try:
            if not isinstance(servicio, Servicio):
                raise ReservaInvalidaError("el objeto no es un Servicio válido")
            self._servicios.append(servicio)
            resultado = True
        except Exception as exc:
            log.error(f"Error al registrar servicio: {exc}")
        finally:
            estado_txt = "OK" if resultado else "FALLIDO"
            nombre_txt = getattr(servicio, "nombre", "desconocido")
            log.debug(f"registrar_servicio('{nombre_txt}') → {estado_txt}")
        return resultado

    def obtener_servicio(self, id_servicio: str) -> Servicio:
        """
        Recupera un servicio por ID.
        Lanza ServicioNoEncontradoError si no existe, encadenando contexto.
        """
        try:
            resultado = next(
                (s for s in self._servicios if s.id == id_servicio), None
            )
            if resultado is None:
                raise ServicioNoEncontradoError(id_servicio)
            return resultado
        except ServicioNoEncontradoError:
            raise
        except Exception as exc:
            raise ServicioNoEncontradoError(id_servicio) from exc

    def listar_servicios(self, solo_activos: bool = True) -> List[Servicio]:
        if solo_activos:
            return [s for s in self._servicios if s.activo]
        return list(self._servicios)

    # ══════════════════════════════════════════════════════════
    # GESTIÓN DE RESERVAS
    # ══════════════════════════════════════════════════════════

    def crear_reserva(
        self,
        id_cliente: str,
        id_servicio: str,
        cantidad: float,
        nota: str = "",
        descuento: float = 0.0
    ) -> Optional[Reserva]:
        """
        Flujo completo de creación de reserva.
        Demuestra: try/except anidado + encadenamiento de excepciones.
        """
        try:
            # Validar existencia de cliente
            cliente = self.obtener_cliente(id_cliente)
            if cliente is None:
                raise ReservaInvalidaError(
                    f"cliente '{id_cliente}' no encontrado"
                )

            # Validar existencia de servicio (puede lanzar ServicioNoEncontradoError)
            try:
                servicio = self.obtener_servicio(id_servicio)
            except ServicioNoEncontradoError as exc:
                raise ReservaInvalidaError(
                    f"servicio no disponible: {exc}"
                ) from exc

            # Detectar duplicados
            if self._existe_reserva_activa(id_cliente, id_servicio):
                raise ReservaDuplicadaError(id_cliente, id_servicio)

            reserva = Reserva(cliente, servicio, cantidad, nota, descuento)

        except (ReservaInvalidaError, ReservaDuplicadaError, CalculoCostoError) as exc:
            log.error(f"Reserva rechazada: {exc}")
            return None
        except Exception as exc:
            log.error(f"Error inesperado al crear reserva: {exc}")
            return None
        else:
            self._reservas.append(reserva)
            return reserva

    def confirmar_reserva(self, id_reserva: str) -> bool:
        """
        Confirma una reserva existente.
        Usa try/except/else/finally.
        """
        confirmada = False
        reserva = None
        try:
            reserva = self._obtener_reserva_o_error(id_reserva)
            reserva.confirmar()
        except EstadoReservaError as exc:
            log.warning(f"Transición inválida: {exc}")
        except ReservaInvalidaError as exc:
            log.error(f"Reserva no encontrada: {exc}")
        except Exception as exc:
            log.error(f"Error inesperado al confirmar: {exc}")
        else:
            confirmada = True
        finally:
            estado = reserva.estado if reserva else "no encontrada"
            log.debug(f"confirmar_reserva('{id_reserva}') → estado actual: {estado}")
        return confirmada

    def cancelar_reserva(self, id_reserva: str, motivo: str = "") -> bool:
        """Cancela una reserva con manejo defensivo de estados."""
        try:
            reserva = self._obtener_reserva_o_error(id_reserva)
            reserva.cancelar(motivo or "sin motivo")
            return True
        except EstadoReservaError as exc:
            log.warning(f"No se puede cancelar: {exc}")
            return False
        except ReservaInvalidaError as exc:
            log.error(str(exc))
            return False
        except Exception as exc:
            log.error(f"Error inesperado al cancelar: {exc}")
            return False

    def calcular_costo_reserva(self, id_reserva: str) -> Optional[float]:
        """Devuelve el costo almacenado en la reserva o None si hay error."""
        try:
            reserva = self._obtener_reserva_o_error(id_reserva)
            return reserva.costo
        except (ReservaInvalidaError, CalculoCostoError) as exc:
            log.error(f"No se pudo calcular costo: {exc}")
            return None

    def listar_reservas(
        self, estado: Optional[str] = None
    ) -> List[Reserva]:
        if estado:
            return [r for r in self._reservas if r.estado == estado]
        return list(self._reservas)

    # ══════════════════════════════════════════════════════════
    # MÉTODOS PRIVADOS DE APOYO
    # ══════════════════════════════════════════════════════════

    def _obtener_reserva_o_error(self, id_reserva: str) -> Reserva:
        reserva = next((r for r in self._reservas if r.id == id_reserva), None)
        if reserva is None:
            raise ReservaInvalidaError(f"reserva '{id_reserva}' no existe")
        return reserva

    def _existe_reserva_activa(self, id_cliente: str, id_servicio: str) -> bool:
        return any(
            r.cliente.id == id_cliente
            and r.servicio.id == id_servicio
            and r.estado != EstadoReserva.CANCELADA
            for r in self._reservas
        )

    # ══════════════════════════════════════════════════════════
    # REPORTE GENERAL
    # ══════════════════════════════════════════════════════════

    def reporte_general(self) -> dict:
        """Genera un snapshot del estado del sistema."""
        pendientes = len(self.listar_reservas(EstadoReserva.PENDIENTE))
        confirmadas = len(self.listar_reservas(EstadoReserva.CONFIRMADA))
        canceladas = len(self.listar_reservas(EstadoReserva.CANCELADA))
        ingresos = sum(
            r.costo for r in self._reservas
            if r.estado == EstadoReserva.CONFIRMADA
        )
        return {
            "clientes_registrados": len(self._clientes),
            "servicios_activos": len(self.listar_servicios()),
            "reservas_pendientes": pendientes,
            "reservas_confirmadas": confirmadas,
            "reservas_canceladas": canceladas,
            "ingresos_confirmados": f"${ingresos:,.2f}",
        }
