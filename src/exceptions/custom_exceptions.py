# ==============================================================
# custom_exceptions.py
# Excepciones personalizadas del sistema Software FJ
# Autor: Software FJ - Equipo de desarrollo
# ==============================================================


class ErrorBase(Exception):
    """
    Clase raíz de todas las excepciones del sistema.
    Centraliza la representación y el código de error.
    """
    def __init__(self, mensaje: str, codigo: int = 0):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo

    def __str__(self) -> str:
        return f"[Error {self.codigo}] {self.mensaje}"


class ClienteInvalidoError(ErrorBase):
    """Se lanza cuando los datos de un cliente no superan la validación."""
    def __init__(self, campo: str, valor_recibido=None):
        detalle = f"Campo '{campo}' inválido."
        if valor_recibido is not None:
            detalle += f" Valor recibido: '{valor_recibido}'"
        super().__init__(detalle, codigo=1001)
        self.campo = campo
        self.valor_recibido = valor_recibido


class ServicioNoEncontradoError(ErrorBase):
    """Se lanza cuando se intenta operar con un servicio que no existe."""
    def __init__(self, id_servicio: str):
        super().__init__(
            f"El servicio con ID '{id_servicio}' no está registrado en el sistema.",
            codigo=2001
        )
        self.id_servicio = id_servicio


class ReservaInvalidaError(ErrorBase):
    """Se lanza cuando los parámetros de una reserva son incorrectos o inconsistentes."""
    def __init__(self, motivo: str):
        super().__init__(f"Reserva rechazada: {motivo}", codigo=3001)
        self.motivo = motivo


class ReservaDuplicadaError(ErrorBase):
    """Se lanza cuando ya existe una reserva activa para el mismo cliente y servicio."""
    def __init__(self, id_cliente: str, id_servicio: str):
        super().__init__(
            f"El cliente '{id_cliente}' ya tiene una reserva activa para el servicio '{id_servicio}'.",
            codigo=3002
        )


class CalculoCostoError(ErrorBase):
    """Se lanza cuando ocurre un fallo durante el cálculo del costo de un servicio."""
    def __init__(self, contexto: str, causa: Exception = None):
        mensaje = f"No se pudo calcular el costo en: {contexto}"
        super().__init__(mensaje, codigo=4001)
        self.__causa = causa

    @property
    def causa_original(self):
        return self.__causa


class CampoVacioError(ClienteInvalidoError):
    """Especialización para campos que llegan vacíos o solo con espacios."""
    def __init__(self, campo: str):
        super().__init__(campo, valor_recibido="<vacío>")
        self.mensaje = f"El campo '{campo}' no puede estar vacío."


class ValorNegativoError(ErrorBase):
    """Se lanza cuando un valor numérico no puede ser negativo (precios, horas, etc.)."""
    def __init__(self, campo: str, valor: float):
        super().__init__(
            f"'{campo}' no admite valores negativos. Recibido: {valor}",
            codigo=5001
        )
        self.campo = campo
        self.valor = valor


class EstadoReservaError(ErrorBase):
    """Se lanza cuando se intenta una transición de estado no permitida en una reserva."""
    def __init__(self, estado_actual: str, operacion: str):
        super().__init__(
            f"No es posible ejecutar '{operacion}' sobre una reserva en estado '{estado_actual}'.",
            codigo=3003
        )
