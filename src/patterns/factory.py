# ==============================================================
# factory.py
# Patrón Factory Method — creación centralizada de servicios
# Desacopla al cliente de los constructores concretos
# ==============================================================

from src.models.servicio import Servicio, ReservaSala, AlquilerEquipo, Asesoria
from src.exceptions.custom_exceptions import ServicioNoEncontradoError
from src.utils.logger import log


class ServicioFactory:
    """
    Fábrica centralizada de objetos Servicio.

    En lugar de instanciar ReservaSala, AlquilerEquipo o Asesoria
    directamente en el código cliente, se delega la responsabilidad
    a esta clase. El beneficio es que agregar un nuevo tipo de servicio
    solo requiere modificar este módulo, no todos los puntos de uso.

    Ejemplo de uso:
        s = ServicioFactory.crear("sala", nombre="Sala Norte",
                                   precio=80000, capacidad=20)
    """

    # Catálogo de tipos soportados → facilita la extensión futura
    _TIPOS_SOPORTADOS = ("sala", "equipo", "asesoria")

    @staticmethod
    def crear(tipo: str, nombre: str, precio: float, **kwargs) -> Servicio:
        """
        Crea e instancia el servicio correspondiente al tipo indicado.

        Parámetros
        ----------
        tipo     : "sala" | "equipo" | "asesoria"
        nombre   : nombre del servicio
        precio   : tarifa base (por hora o por día según el tipo)
        **kwargs : argumentos específicos del subtipo
                   - sala     → capacidad: int
                   - equipo   → incluye_seguro: bool = False
                   - asesoria → nivel: str = "senior"

        Lanza
        -----
        ServicioNoEncontradoError si el tipo no está registrado.
        """
        tipo_normalizado = tipo.strip().lower()

        if tipo_normalizado == "sala":
            capacidad = kwargs.get("capacidad", 10)
            servicio = ReservaSala(nombre, precio, capacidad)

        elif tipo_normalizado == "equipo":
            incluye_seguro = kwargs.get("incluye_seguro", False)
            servicio = AlquilerEquipo(nombre, precio, incluye_seguro)

        elif tipo_normalizado == "asesoria":
            nivel = kwargs.get("nivel", "senior")
            servicio = Asesoria(nombre, precio, nivel)

        else:
            raise ServicioNoEncontradoError(
                f"tipo='{tipo}' — tipos válidos: {ServicioFactory._TIPOS_SOPORTADOS}"
            )

        log.info(f"Factory: servicio creado → {servicio!r}")
        return servicio

    @staticmethod
    def tipos_disponibles() -> tuple:
        """Devuelve los tipos de servicio registrados en la fábrica."""
        return ServicioFactory._TIPOS_SOPORTADOS

