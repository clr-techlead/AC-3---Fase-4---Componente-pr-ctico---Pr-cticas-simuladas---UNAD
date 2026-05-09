# ==============================================================
# simulacion.py
# 12 operaciones que cubren casos exitosos y escenarios de error
# El sistema debe seguir ejecutándose ante cada fallo
# ==============================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.gestion_reservas import GestionReservas
from src.models.servicio import ReservaSala, AlquilerEquipo, Asesoria
from src.utils.logger import log


def separador(titulo: str) -> None:
    print(f"\n{'─' * 55}")
    print(f"  {titulo}")
    print('─' * 55)


def ejecutar_simulacion():
    sistema = GestionReservas()

    # ══════════════════════════════════════════════════════════
    # BLOQUE 1 — Registro de servicios
    # ══════════════════════════════════════════════════════════
    separador("OP 1 | Registrar servicios válidos")
    sala = ReservaSala("Sala Alfa", precio_por_hora=60_000, capacidad=15)
    equipo = AlquilerEquipo("Proyector Epson", precio_por_dia=30_000, incluye_seguro=False)
    asesoria = Asesoria("Asesoría Cloud", tarifa_hora=150_000, nivel="experto")

    ok1 = sistema.registrar_servicio(sala)
    ok2 = sistema.registrar_servicio(equipo)
    ok3 = sistema.registrar_servicio(asesoria)
    print(f"  Sala registrada     : {ok1}")
    print(f"  Equipo registrado   : {ok2}")
    print(f"  Asesoría registrada : {ok3}")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 2 — Registro de clientes
    # ══════════════════════════════════════════════════════════
    separador("OP 2 | Registrar clientes válidos")
    c1 = sistema.registrar_cliente("Laura Suárez", "laura@correo.co", "3151234567")
    c2 = sistema.registrar_cliente("Pedro Molina", "pedro.m@empresa.com", "+573209876543")
    print(f"  Cliente 1: {c1}")
    print(f"  Cliente 2: {c2}")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 3 — Error: email duplicado
    # ══════════════════════════════════════════════════════════
    separador("OP 3 | Intentar registrar email duplicado (debe fallar)")
    c_dup = sistema.registrar_cliente("Laura Duplicada", "laura@correo.co", "3001111111")
    print(f"  Resultado esperado None → obtenido: {c_dup}")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 4 — Error: datos de cliente inválidos
    # ══════════════════════════════════════════════════════════
    separador("OP 4 | Registrar cliente con email inválido (debe fallar)")
    c_bad = sistema.registrar_cliente("Sin Email", "no-es-un-email", "3001234567")
    print(f"  Resultado esperado None → obtenido: {c_bad}")

    separador("OP 5 | Registrar cliente con nombre vacío (debe fallar)")
    c_empty = sistema.registrar_cliente("", "vacio@test.com", "3001234567")
    print(f"  Resultado esperado None → obtenido: {c_empty}")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 5 — Crear reservas exitosas
    # ══════════════════════════════════════════════════════════
    separador("OP 6 | Crear reserva de sala para Laura (3 horas)")
    r1 = None
    if c1:
        r1 = sistema.crear_reserva(c1.id, sala.id, cantidad=3.0, nota="Reunión de equipo")
        if r1:
            print(f"  {r1}")
            print(f"  Costo: {r1.costo:,.2f} COP")

    separador("OP 7 | Crear reserva de equipo para Pedro (5 días, 10% descuento)")
    r2 = None
    if c2:
        r2 = sistema.crear_reserva(c2.id, equipo.id, cantidad=5.0, descuento=0.10,
                                   nota="Evento corporativo")
        if r2:
            print(f"  {r2}")
            print(f"  Costo: {r2.costo:,.2f} COP")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 6 — Error: reserva duplicada
    # ══════════════════════════════════════════════════════════
    separador("OP 8 | Intentar duplicar reserva de sala para Laura (debe fallar)")
    if c1:
        r_dup = sistema.crear_reserva(c1.id, sala.id, cantidad=1.0)
        print(f"  Resultado esperado None → obtenido: {r_dup}")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 7 — Error: cantidad negativa
    # ══════════════════════════════════════════════════════════
    separador("OP 9 | Crear reserva con horas negativas (debe fallar)")
    if c1:
        r_neg = sistema.crear_reserva(c1.id, asesoria.id, cantidad=-2.0)
        print(f"  Resultado esperado None → obtenido: {r_neg}")

    # ══════════════════════════════════════════════════════════
    # BLOQUE 8 — Confirmar y cancelar reservas
    # ══════════════════════════════════════════════════════════
    separador("OP 10 | Confirmar reserva de sala")
    if r1:
        ok = sistema.confirmar_reserva(r1.id)
        print(f"  Confirmada: {ok} | Estado: {r1.estado}")

    separador("OP 11 | Intentar confirmar reserva ya confirmada (debe fallar)")
    if r1:
        ok2 = sistema.confirmar_reserva(r1.id)
        print(f"  Resultado esperado False → obtenido: {ok2}")

    separador("OP 12 | Cancelar reserva de equipo")
    if r2:
        ok3 = sistema.cancelar_reserva(r2.id, "Cliente canceló el evento")
        print(f"  Cancelada: {ok3} | Estado: {r2.estado}")

    # ══════════════════════════════════════════════════════════
    # REPORTE FINAL
    # ══════════════════════════════════════════════════════════
    separador("REPORTE GENERAL DEL SISTEMA")
    reporte = sistema.reporte_general()
    for k, v in reporte.items():
        print(f"  {k:<32}: {v}")

    separador("SISTEMA FUNCIONANDO CORRECTAMENTE")
    print("  Todos los errores fueron manejados.")
    print("  Revisa logs/app.log para el historial completo.\n")


if __name__ == "__main__":
    ejecutar_simulacion()
    