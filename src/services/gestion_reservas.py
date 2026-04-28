# ==============================================================
# gestion_reservas.py  v2.0
# Capa de servicio — orquesta clientes, servicios y reservas
# Incorpora: Context Manager, patrón Observer, Facturación
# ==============================================================

from typing import List, Optional
from src.models.cliente import Cliente
from src.models.servicio import Servicio
from src.models.reserva import Reserva, EstadoReserva
from src.models.factura import Factura
from src.patterns.observer import Observable
from src.exceptions.custom_exceptions import (
    ClienteInvalidoError, ServicioNoEncontradoError,
    ReservaInvalidaError, ReservaDuplicadaError,
    EstadoReservaError, CalculoCostoError
)
from src.utils.logger import log


class GestionReservas(Observable):
    """
    Fachada principal del sistema Software FJ.

    Mejoras v2.0:
    - Hereda Observable: emite eventos a observadores suscritos
    - Implementa Context Manager (__enter__ / __exit__)
    - Genera facturas automáticamente al confirmar una reserva
    - Historial de facturas consultable
    """

    def __init__(self):
        super().__init__()   # Inicializa la lista de observadores
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._facturas: List[Factura] = []
        log.info("Sistema Software FJ v2.0 iniciado.")

    # ── Context Manager ───────────────────────────────────────
    def __enter__(self):
        """Permite usar el sistema con el bloque with."""
        log.debug("GestionReservas: entrando al bloque with")
        return self

    def __exit__(self, tipo_exc, valor_exc, traceback):
        """
        Cierra el contexto. Si ocurrió una excepción, la registra
        en el log pero no la suprime (retorna False).
        """
        if tipo_exc:
            log.error(f"GestionReservas: excepción en bloque with: {valor_exc}")
        else:
            log.debug("GestionReservas: bloque with finalizado sin errores")
        return False

    # ══════════════════════════════════════════════════════════
    # GESTIÓN DE CLIENTES
    # ══════════════════════════════════════════════════════════

    def registrar_cliente(self, nombre: str, email: str, telefono: str) -> Optional[Cliente]:
        try:
            if self._buscar_cliente_por_email(email):
                raise ClienteInvalidoError("email", f"{email} ya registrado")
            cliente = Cliente(nombre, email, telefono)
        except ClienteInvalidoError as exc:
            log.error(f"No se pudo registrar cliente: {exc}")
            return None
        except Exception as exc:
            log.error(f"Error inesperado al registrar cliente: {exc}")
            return None
        else:
            self._clientes.append(cliente)
            self.notificar("cliente_registrado", {"cliente": cliente.nombre})
            return cliente

    def obtener_cliente(self, id_cliente: str) -> Optional[Cliente]:
        return next((c for c in self._clientes if c.id == id_cliente), None)

    def listar_clientes(self) -> List[Cliente]:
        return list(self._clientes)

    def _buscar_cliente_por_email(self, email: str) -> Optional[Cliente]:
        return next(
            (c for c in self._clientes if c.email == email.strip().lower()), None
        )

    # ══════════════════════════════════════════════════════════
    # GESTIÓN DE SERVICIOS
    # ══════════════════════════════════════════════════════════

    def registrar_servicio(self, servicio: Servicio) -> bool:
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
            log.debug(f"registrar_servicio → {estado_txt}")
        return resultado

    def obtener_servicio(self, id_servicio: str) -> Servicio:
        try:
            resultado = next((s for s in self._servicios if s.id == id_servicio), None)
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
        try:
            cliente = self.obtener_cliente(id_cliente)
            if cliente is None:
                raise ReservaInvalidaError(f"cliente '{id_cliente}' no encontrado")
            try:
                servicio = self.obtener_servicio(id_servicio)
            except ServicioNoEncontradoError as exc:
                raise ReservaInvalidaError(f"servicio no disponible: {exc}") from exc
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
            self.notificar("reserva_creada", {
                "reserva_id": reserva.id,
                "cliente": cliente.nombre,
                "email": cliente.email,
                "servicio": servicio.nombre,
                "costo": f"${reserva.costo:,.2f}",
            })
            return reserva

    def confirmar_reserva(self, id_reserva: str) -> bool:
        confirmada = False
        reserva = None
        try:
            reserva = self._obtener_reserva_o_error(id_reserva)
            reserva.confirmar()
            # Generar factura automáticamente al confirmar
            factura = Factura(reserva)
            self._facturas.append(factura)
        except EstadoReservaError as exc:
            log.warning(f"Transición inválida: {exc}")
        except ReservaInvalidaError as exc:
            log.error(f"Reserva no encontrada: {exc}")
        except Exception as exc:
            log.error(f"Error inesperado al confirmar: {exc}")
        else:
            confirmada = True
            self.notificar("reserva_confirmada", {
                "reserva_id": reserva.id,
                "cliente": reserva.cliente.nombre,
                "email": reserva.cliente.email,
                "servicio": reserva.servicio.nombre,
                "costo": f"${reserva.costo:,.2f}",
            })
        finally:
            estado = reserva.estado if reserva else "no encontrada"
            log.debug(f"confirmar_reserva('{id_reserva}') → {estado}")
        return confirmada

    def cancelar_reserva(self, id_reserva: str, motivo: str = "") -> bool:
        try:
            reserva = self._obtener_reserva_o_error(id_reserva)
            reserva.cancelar(motivo or "sin motivo")
            self.notificar("reserva_cancelada", {
                "reserva_id": reserva.id,
                "cliente": reserva.cliente.nombre,
                "email": reserva.cliente.email,
                "servicio": reserva.servicio.nombre,
                "motivo": motivo,
            })
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
        try:
            reserva = self._obtener_reserva_o_error(id_reserva)
            return reserva.costo
        except (ReservaInvalidaError, CalculoCostoError) as exc:
            log.error(f"No se pudo calcular costo: {exc}")
            return None

    def listar_reservas(self, estado: Optional[str] = None) -> List[Reserva]:
        if estado:
            return [r for r in self._reservas if r.estado == estado]
        return list(self._reservas)

    def listar_facturas(self) -> List[Factura]:
        return list(self._facturas)

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
        pendientes  = len(self.listar_reservas(EstadoReserva.PENDIENTE))
        confirmadas = len(self.listar_reservas(EstadoReserva.CONFIRMADA))
        canceladas  = len(self.listar_reservas(EstadoReserva.CANCELADA))
        ingresos    = sum(
            r.costo for r in self._reservas
            if r.estado == EstadoReserva.CONFIRMADA
        )
        return {
            "clientes_registrados": len(self._clientes),
            "servicios_activos":    len(self.listar_servicios()),
            "reservas_pendientes":  pendientes,
            "reservas_confirmadas": confirmadas,
            "reservas_canceladas":  canceladas,
            "facturas_emitidas":    len(self._facturas),
            "ingresos_confirmados": f"${ingresos:,.2f}",
        }
