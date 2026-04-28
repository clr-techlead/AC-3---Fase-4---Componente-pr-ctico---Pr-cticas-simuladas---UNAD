# ==============================================================
# exportador.py
# Exportación de datos a CSV y búsqueda/filtrado avanzado
# Usa solo módulos estándar: csv, os, datetime
# ==============================================================

import csv
import os
from datetime import datetime, date
from typing import List, Optional
from src.utils.logger import log


class ExportadorCSV:
    """
    Exporta colecciones de objetos del sistema a archivos CSV.
    Crea el directorio de destino automáticamente si no existe.
    """

    def __init__(self, directorio_salida: str = "exports"):
        self._directorio = directorio_salida
        os.makedirs(directorio_salida, exist_ok=True)

    def exportar_reservas(self, reservas: list, nombre_archivo: str = "") -> str:
        """
        Exporta una lista de objetos Reserva a CSV.
        Devuelve la ruta del archivo generado.
        """
        if not nombre_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reservas_{timestamp}.csv"

        ruta = os.path.join(self._directorio, nombre_archivo)
        campos = ["id", "estado", "cliente", "servicio",
                  "cantidad", "descuento_pct", "costo_total", "creada", "nota"]

        try:
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                for r in reservas:
                    writer.writerow(r.resumen())
            log.info(f"CSV exportado: {ruta} ({len(reservas)} filas)")
        except OSError as exc:
            log.error(f"No se pudo exportar CSV: {exc}")
            raise
        return ruta

    def exportar_facturas(self, facturas: list, nombre_archivo: str = "") -> str:
        """Exporta una lista de objetos Factura a CSV."""
        if not nombre_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"facturas_{timestamp}.csv"

        ruta = os.path.join(self._directorio, nombre_archivo)
        if not facturas:
            log.warning("No hay facturas para exportar.")
            return ruta

        campos = list(facturas[0].to_dict().keys())
        try:
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                for factura in facturas:
                    writer.writerow(factura.to_dict())
            log.info(f"CSV facturas exportado: {ruta} ({len(facturas)} filas)")
        except OSError as exc:
            log.error(f"Error exportando facturas: {exc}")
            raise
        return ruta


class BuscadorReservas:
    """
    Motor de búsqueda y filtrado sobre colecciones de Reserva.
    Todos los métodos devuelven listas nuevas sin modificar la original.
    """

    def __init__(self, reservas: list):
        self._reservas = reservas

    def por_estado(self, estado: str) -> list:
        """Filtra reservas por estado exacto (PENDIENTE / CONFIRMADA / CANCELADA)."""
        return [r for r in self._reservas if r.estado == estado.upper()]

    def por_cliente(self, nombre_parcial: str) -> list:
        """Búsqueda case-insensitive por nombre de cliente."""
        termino = nombre_parcial.strip().lower()
        return [r for r in self._reservas
                if termino in r.cliente.nombre.lower()]

    def por_servicio(self, nombre_parcial: str) -> list:
        """Búsqueda case-insensitive por nombre de servicio."""
        termino = nombre_parcial.strip().lower()
        return [r for r in self._reservas
                if termino in r.servicio.nombre.lower()]

    def por_rango_fechas(self,
                         desde: date,
                         hasta: Optional[date] = None) -> list:
        """
        Filtra reservas cuya fecha de creación esté en el rango [desde, hasta].
        Si no se indica "hasta", se usa la fecha de hoy.
        """
        hasta = hasta or date.today()
        return [
            r for r in self._reservas
            if desde <= r.fecha_creacion.date() <= hasta
        ]

    def por_costo_minimo(self, monto: float) -> list:
        """Devuelve reservas cuyo costo total supera el monto indicado."""
        return [r for r in self._reservas if r.costo >= monto]

    def ordenar_por_costo(self, ascendente: bool = True) -> list:
        """Devuelve todas las reservas ordenadas por costo."""
        return sorted(self._reservas, key=lambda r: r.costo, reverse=not ascendente)

    def busqueda_combinada(self,
                           estado: Optional[str] = None,
                           cliente: Optional[str] = None,
                           costo_minimo: Optional[float] = None) -> list:
        """
        Aplica múltiples filtros en cadena.
        Solo aplica los filtros que tengan valor (los None se ignoran).
        """
        resultado = list(self._reservas)
        if estado:
            resultado = [r for r in resultado if r.estado == estado.upper()]
        if cliente:
            termino = cliente.lower()
            resultado = [r for r in resultado if termino in r.cliente.nombre.lower()]
        if costo_minimo is not None:
            resultado = [r for r in resultado if r.costo >= costo_minimo]
        log.debug(f"Búsqueda combinada: {len(resultado)} resultados")
        return resultado
