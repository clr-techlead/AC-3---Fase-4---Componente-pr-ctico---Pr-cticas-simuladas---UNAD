# ==============================================================
# main.py
# Punto de entrada del sistema Software FJ
# Demuestra el flujo completo: registrar, reservar, confirmar
# ==============================================================

import sys
import os

# Asegurar que Python encuentre el paquete src desde cualquier directorio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.gestion_reservas import GestionReservas
from src.models.servicio import ReservaSala, AlquilerEquipo, Asesoria
from src.utils.logger import log


def main():
    print("=" * 60)
    print("   SISTEMA DE RESERVAS — Software FJ")
    print("=" * 60)

    sistema = GestionReservas()

    # ── 1. Registrar servicios ────────────────────────────────
    sala_principal = ReservaSala("Sala Innovación", precio_por_hora=80_000, capacidad=20)
    laptop_dell = AlquilerEquipo("Laptop Dell XPS", precio_por_dia=45_000, incluye_seguro=True)
    asesoria_tech = Asesoria("Consultoría DevOps", tarifa_hora=120_000, nivel="experto")

    sistema.registrar_servicio(sala_principal)
    sistema.registrar_servicio(laptop_dell)
    sistema.registrar_servicio(asesoria_tech)

    # ── 2. Registrar clientes ─────────────────────────────────
    c1 = sistema.registrar_cliente("Ana María Torres", "ana.torres@correo.com", "3001234567")
    c2 = sistema.registrar_cliente("Carlos Rueda", "c.rueda@empresa.co", "+573009876543")

    # ── 3. Crear reservas ─────────────────────────────────────
    if c1 and c2:
        r1 = sistema.crear_reserva(c1.id, sala_principal.id, cantidad=3.0,
                                   nota="Reunión de lanzamiento")
        r2 = sistema.crear_reserva(c2.id, laptop_dell.id, cantidad=5.0,
                                   descuento=0.10, nota="Proyecto beta")
        r3 = sistema.crear_reserva(c1.id, asesoria_tech.id, cantidad=2.0)

        # ── 4. Confirmar y cancelar ───────────────────────────
        if r1:
            sistema.confirmar_reserva(r1.id)
        if r2:
            sistema.confirmar_reserva(r2.id)
        if r3:
            sistema.cancelar_reserva(r3.id, "Presupuesto insuficiente")

    # ── 5. Reporte final ──────────────────────────────────────
    print()
    reporte = sistema.reporte_general()
    print("── REPORTE GENERAL ──────────────────────────────────")
    for clave, valor in reporte.items():
        print(f"  {clave:<30}: {valor}")
    print("=" * 60)
    print("Consulta logs/app.log para el historial completo.")
    print("=" * 60)

    log.info("Ejecución de main.py finalizada correctamente.")


if __name__ == "__main__":
    main()
