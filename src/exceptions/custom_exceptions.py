# ==============================================================
# custom_exceptions.py
# Excepciones personalizadas del sistema Software FJ
# Autor: Software FJ - Equipo de desarrollo
# ==============================================================


class ErrorBase(Exception):
    """
    Clase base de todas las excepciones del sistema.
    Centraliza el manejo de mensajes y códigos de error.
    """

    def __init__(self, mensaje: str, codigo: int = 0):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo

    def __str__(self):
        return f"[ERROR {self.codigo}] {self.mensaje}"


# ==============================================================
# EXCEPCIONES RELACIONADAS CON CLIENTES
# ==============================================================

class ClienteInvalidoError(ErrorBase):
    """
    Se lanza cuando un cliente tiene datos inválidos.
    """

    def __init__(self, campo: str, valor_recibido=None):
        mensaje = f"El campo '{campo}' es inválido."

        if valor_recibido is not None:
            mensaje += f" Valor recibido: '{valor_recibido}'"

        super().__init__(mensaje, codigo=1001)

        self.campo = campo
        self.valor_recibido = valor_recibido


class CampoVacioError(ClienteInvalidoError):
    """
    Se lanza cuando un campo obligatorio está vacío.
    """

    def __init__(self, campo: str):
        mensaje = f"El campo '{campo}' no puede estar vacío."

        super().__init__(campo, valor_recibido="<vacío>")

        self.mensaje = mensaje
        self.args = (mensaje,)


# ==============================================================
# EXCEPCIONES RELACIONADAS CON SERVICIOS
# ==============================================================

class ServicioNoEncontradoError(ErrorBase):
    """
    Se lanza cuando un servicio no existe.
    """

    def __init__(self, id_servicio: str):

        super().__init__(
            f"El servicio con ID '{id_servicio}' no existe en el sistema.",
            codigo=2001
        )

        self.id_servicio = id_servicio


class ServicioNoDisponibleError(ErrorBase):
    """
    Se lanza cuando un servicio no está disponible.
    """

    def __init__(self, nombre_servicio: str):

        super().__init__(
            f"El servicio '{nombre_servicio}' no se encuentra disponible.",
            codigo=2002
        )

        self.nombre_servicio = nombre_servicio


# ==============================================================
# EXCEPCIONES RELACIONADAS CON RESERVAS
# ==============================================================

class ReservaInvalidaError(ErrorBase):
    """
    Se lanza cuando una reserva contiene datos inválidos.
    """

    def __init__(self, motivo: str):

        super().__init__(
            f"Reserva inválida: {motivo}",
            codigo=3001
        )

        self.motivo = motivo


class ReservaDuplicadaError(ErrorBase):
    """
    Se lanza cuando ya existe una reserva activa
    para el mismo cliente y servicio.
    """

    def __init__(self, id_cliente: str, id_servicio: str):

        super().__init__(
            f"El cliente '{id_cliente}' ya tiene "
            f"una reserva activa para el servicio '{id_servicio}'.",
            codigo=3002
        )

        self.id_cliente = id_cliente
        self.id_servicio = id_servicio


class EstadoReservaError(ErrorBase):
    """
    Se lanza cuando se intenta una operación inválida
    según el estado actual de la reserva.
    """

    def __init__(self, estado_actual: str, operacion: str):

        super().__init__(
            f"No es posible ejecutar '{operacion}' "
            f"sobre una reserva en estado '{estado_actual}'.",
            codigo=3003
        )

        self.estado_actual = estado_actual
        self.operacion = operacion


class DuracionInvalidaError(ErrorBase):
    """
    Se lanza cuando la duración de una reserva es incorrecta.
    """

    def __init__(self, duracion):

        super().__init__(
            f"La duración '{duracion}' no es válida.",
            codigo=3004
        )

        self.duracion = duracion


class ProcesamientoReservaError(ErrorBase):
    """
    Error general durante el procesamiento de reservas.
    """

    def __init__(self, detalle: str):

        super().__init__(
            f"Error procesando reserva: {detalle}",
            codigo=3005
        )

        self.detalle = detalle


# ==============================================================
# EXCEPCIONES RELACIONADAS CON CÁLCULOS
# ==============================================================

class CalculoCostoError(ErrorBase):
    """
    Se lanza cuando ocurre un error calculando costos.
    """

    def __init__(self, contexto: str, causa: Exception = None):

        mensaje = f"No se pudo calcular el costo en '{contexto}'."

        super().__init__(mensaje, codigo=4001)

        self.__causa = causa

    @property
    def causa_original(self):
        return self.__causa


class ValorNegativoError(ErrorBase):
    """
    Se lanza cuando un valor numérico es negativo.
    """

    def __init__(self, campo: str, valor: float):

        super().__init__(
            f"El campo '{campo}' no admite valores negativos. "
            f"Valor recibido: {valor}",
            codigo=5001
        )

        self.campo = campo
        self.valor = valor
        