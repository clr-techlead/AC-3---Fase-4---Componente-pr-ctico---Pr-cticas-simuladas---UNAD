# ==============================================================
# gestion_reservas.py  v3.0
# Capa de servicio principal del sistema Software FJ
# ==============================================================

from typing import List, Optional

from src.models.cliente import Cliente
from src.models.servicio import Servicio
from src.models.reserva import Reserva, EstadoReserva
from src.models.factura import Factura

from src.patterns.observer import Observable

from src.exceptions.custom_exceptions import (
    ClienteInvalidoError,
    ServicioNoEncontradoError,
    ReservaInvalidaError,
    ReservaDuplicadaError,
    EstadoReservaError,
    CalculoCostoError
)

from src.utils.logger import log


class GestionReservas(Observable):
    """
    Clase principal del sistema Software FJ.

    Funcionalidades:
    - Gestión de clientes
    - Gestión de servicios
    - Gestión de reservas
    - Facturación automática
    - Observer Pattern
    - Context Manager
    - Manejo robusto de excepciones
    """

    # ==========================================================
    # CONSTRUCTOR
    # ==========================================================

    def __init__(self):

        super().__init__()

        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._facturas: List[Factura] = []

        log.info("Sistema Software FJ iniciado correctamente")

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self):

        log.info("Entrando al contexto del sistema")

        return self

    def __exit__(self, tipo_exc, valor_exc, traceback):

        if tipo_exc:

            log.error(
                f"Error dentro del contexto: {valor_exc}"
            )

        else:

            log.info(
                "Cierre correcto del contexto"
            )

        return False

    # ==========================================================
    # GESTIÓN DE CLIENTES
    # ==========================================================

    def registrar_cliente(
        self,
        nombre: str,
        email: str,
        telefono: str
    ) -> Optional[Cliente]:

        try:

            # ----------------------------------------------
            # Validar email duplicado
            # ----------------------------------------------

            if self._buscar_cliente_por_email(email):

                raise ClienteInvalidoError(
                    "email",
                    f"{email} ya registrado"
                )

            # ----------------------------------------------
            # Crear cliente
            # ----------------------------------------------

            cliente = Cliente(
                nombre,
                email,
                telefono
            )

        except ClienteInvalidoError as exc:

            log.error(
                f"No se pudo registrar cliente: {exc}"
            )

            return None

        except Exception as exc:

            log.error(
                f"Error inesperado registrando cliente: {exc}"
            )

            return None

        else:

            self._clientes.append(cliente)

            self.notificar(
                "cliente_registrado",
                {
                    "cliente": cliente.nombre,
                    "email": cliente.email
                }
            )

            log.info(
                f"Cliente registrado: {cliente.id}"
            )

            return cliente

    def obtener_cliente(
        self,
        id_cliente: str
    ) -> Optional[Cliente]:

        return next(
            (
                c for c in self._clientes
                if c.id == id_cliente
            ),
            None
        )

    def listar_clientes(self) -> List[Cliente]:

        return list(self._clientes)

    def _buscar_cliente_por_email(
        self,
        email: str
    ) -> Optional[Cliente]:

        return next(
            (
                c for c in self._clientes
                if c.email == email.strip().lower()
            ),
            None
        )

    # ==========================================================
    # GESTIÓN DE SERVICIOS
    # ==========================================================

    def registrar_servicio(
        self,
        servicio: Servicio
    ) -> bool:

        resultado = False

        try:

            # ----------------------------------------------
            # Validar tipo
            # ----------------------------------------------

            if not isinstance(servicio, Servicio):

                raise ReservaInvalidaError(
                    "el objeto recibido no es un servicio válido"
                )

            # ----------------------------------------------
            # Evitar duplicados
            # ----------------------------------------------

            existe = any(
                s.nombre == servicio.nombre
                for s in self._servicios
            )

            if existe:

                raise ReservaInvalidaError(
                    f"el servicio '{servicio.nombre}' ya existe"
                )

            # ----------------------------------------------
            # Registrar
            # ----------------------------------------------

            self._servicios.append(servicio)

            resultado = True

        except Exception as exc:

            log.error(
                f"Error registrando servicio: {exc}"
            )

        finally:

            estado = "OK" if resultado else "FALLIDO"

            log.debug(
                f"registrar_servicio → {estado}"
            )

        return resultado

    def obtener_servicio(
        self,
        id_servicio: str
    ) -> Servicio:

        try:

            servicio = next(
                (
                    s for s in self._servicios
                    if s.id == id_servicio
                ),
                None
            )

            if servicio is None:

                raise ServicioNoEncontradoError(
                    id_servicio
                )

            return servicio

        except ServicioNoEncontradoError:

            raise

        except Exception as exc:

            raise ServicioNoEncontradoError(
                id_servicio
            ) from exc

    def listar_servicios(
        self,
        solo_activos: bool = True
    ) -> List[Servicio]:

        if solo_activos:

            return [
                s for s in self._servicios
                if s.activo
            ]

        return list(self._servicios)

    # ==========================================================
    # GESTIÓN DE RESERVAS
    # ==========================================================

    def crear_reserva(
        self,
        id_cliente: str,
        id_servicio: str,
        cantidad: float,
        nota: str = "",
        descuento: float = 0.0
    ) -> Optional[Reserva]:

        try:

            # ----------------------------------------------
            # Validar cliente
            # ----------------------------------------------

            cliente = self.obtener_cliente(
                id_cliente
            )

            if cliente is None:

                raise ReservaInvalidaError(
                    f"cliente '{id_cliente}' no encontrado"
                )

            # ----------------------------------------------
            # Validar servicio
            # ----------------------------------------------

            try:

                servicio = self.obtener_servicio(
                    id_servicio
                )

            except ServicioNoEncontradoError as exc:

                raise ReservaInvalidaError(
                    f"servicio no disponible: {exc}"
                ) from exc

            # ----------------------------------------------
            # Validar servicio activo
            # ----------------------------------------------

            if not servicio.activo:

                raise ReservaInvalidaError(
                    "el servicio se encuentra inactivo"
                )

            # ----------------------------------------------
            # Validar cantidad
            # ----------------------------------------------

            if cantidad <= 0:

                raise ReservaInvalidaError(
                    "la cantidad debe ser mayor a cero"
                )

            # ----------------------------------------------
            # Validar reserva duplicada
            # ----------------------------------------------

            if self._existe_reserva_activa(
                id_cliente,
                id_servicio
            ):

                raise ReservaDuplicadaError(
                    id_cliente,
                    id_servicio
                )

            # ----------------------------------------------
            # Crear reserva
            # ----------------------------------------------

            reserva = Reserva(
                cliente,
                servicio,
                cantidad,
                nota,
                descuento
            )

        except (
            ReservaInvalidaError,
            ReservaDuplicadaError,
            CalculoCostoError
        ) as exc:

            log.error(
                f"Reserva rechazada: {exc}"
            )

            return None

        except Exception as exc:

            log.error(
                f"Error inesperado creando reserva: {exc}"
            )

            return None

        else:

            self._reservas.append(reserva)

            self.notificar(
                "reserva_creada",
                {
                    "reserva_id": reserva.id,
                    "cliente": cliente.nombre,
                    "email": cliente.email,
                    "servicio": servicio.nombre,
                    "costo": f"${reserva.costo:,.2f}"
                }
            )

            log.info(
                f"Reserva creada correctamente: {reserva.id}"
            )

            return reserva

    def confirmar_reserva(
        self,
        id_reserva: str
    ) -> bool:

        confirmada = False
        reserva = None

        try:

            reserva = self._obtener_reserva_o_error(
                id_reserva
            )

            reserva.confirmar()

            # ----------------------------------------------
            # Generar factura automática
            # ----------------------------------------------

            factura = Factura(reserva)

            self._facturas.append(factura)

        except EstadoReservaError as exc:

            log.warning(
                f"Estado inválido: {exc}"
            )

        except ReservaInvalidaError as exc:

            log.error(
                f"Reserva inválida: {exc}"
            )

        except Exception as exc:

            log.error(
                f"Error inesperado confirmando reserva: {exc}"
            )

        else:

            confirmada = True

            self.notificar(
                "reserva_confirmada",
                {
                    "reserva_id": reserva.id,
                    "cliente": reserva.cliente.nombre,
                    "servicio": reserva.servicio.nombre,
                    "costo": f"${reserva.costo:,.2f}"
                }
            )

        finally:

            estado = (
                reserva.estado
                if reserva
                else "NO ENCONTRADA"
            )

            log.debug(
                f"confirmar_reserva → {estado}"
            )

        return confirmada

    def cancelar_reserva(
        self,
        id_reserva: str,
        motivo: str = ""
    ) -> bool:

        try:

            reserva = self._obtener_reserva_o_error(
                id_reserva
            )

            reserva.cancelar(
                motivo or "Sin motivo"
            )

            self.notificar(
                "reserva_cancelada",
                {
                    "reserva_id": reserva.id,
                    "cliente": reserva.cliente.nombre,
                    "motivo": motivo
                }
            )

            return True

        except EstadoReservaError as exc:

            log.warning(
                f"No se puede cancelar: {exc}"
            )

            return False

        except ReservaInvalidaError as exc:

            log.error(str(exc))

            return False

        except Exception as exc:

            log.error(
                f"Error inesperado cancelando reserva: {exc}"
            )

            return False

    def calcular_costo_reserva(
        self,
        id_reserva: str
    ) -> Optional[float]:

        try:

            reserva = self._obtener_reserva_o_error(
                id_reserva
            )

            return reserva.costo

        except (
            ReservaInvalidaError,
            CalculoCostoError
        ) as exc:

            log.error(
                f"No se pudo calcular costo: {exc}"
            )

            return None

    def listar_reservas(
        self,
        estado: Optional[EstadoReserva] = None
    ) -> List[Reserva]:

        if estado:

            return [
                r for r in self._reservas
                if r.estado == estado
            ]

        return list(self._reservas)

    # ==========================================================
    # FACTURAS
    # ==========================================================

    def listar_facturas(self) -> List[Factura]:

        return list(self._facturas)

    # ==========================================================
    # MÉTODOS PRIVADOS
    # ==========================================================

    def _obtener_reserva_o_error(
        self,
        id_reserva: str
    ) -> Reserva:

        reserva = next(
            (
                r for r in self._reservas
                if r.id == id_reserva
            ),
            None
        )

        if reserva is None:

            raise ReservaInvalidaError(
                f"reserva '{id_reserva}' no existe"
            )

        return reserva

    def _existe_reserva_activa(
        self,
        id_cliente: str,
        id_servicio: str
    ) -> bool:

        return any(
            r.cliente.id == id_cliente
            and r.servicio.id == id_servicio
            and r.estado != EstadoReserva.CANCELADA
            for r in self._reservas
        )

    # ==========================================================
    # REPORTES
    # ==========================================================

    def reporte_general(self) -> dict:

        pendientes = len(
            self.listar_reservas(
                EstadoReserva.PENDIENTE
            )
        )

        confirmadas = len(
            self.listar_reservas(
                EstadoReserva.CONFIRMADA
            )
        )

        canceladas = len(
            self.listar_reservas(
                EstadoReserva.CANCELADA
            )
        )

        ingresos = sum(
            r.costo
            for r in self._reservas
            if r.estado == EstadoReserva.CONFIRMADA
        )

        return {
            "clientes_registrados": len(self._clientes),
            "servicios_activos": len(
                self.listar_servicios()
            ),
            "reservas_pendientes": pendientes,
            "reservas_confirmadas": confirmadas,
            "reservas_canceladas": canceladas,
            "facturas_emitidas": len(self._facturas),
            "ingresos_confirmados": f"${ingresos:,.2f}"
        }