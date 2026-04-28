# ==============================================================
# test_reserva.py
# Pruebas unitarias para Reserva: ciclo de estados, costos, validaciones
# ==============================================================

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from src.models.cliente import Cliente
from src.models.servicio import ReservaSala, AlquilerEquipo, Asesoria
from src.models.reserva import Reserva, EstadoReserva
from src.exceptions.custom_exceptions import (
    ReservaInvalidaError, EstadoReservaError, ValorNegativoError
)


class TestReservaSetUp(unittest.TestCase):
    """Base con objetos reutilizables para todos los tests."""

    def setUp(self):
        self.cliente = Cliente("Laura Ruiz", "laura@ok.com", "3001234567")
        self.sala = ReservaSala("Sala A", 60_000, 10)
        self.equipo = AlquilerEquipo("Laptop", 40_000, False)
        self.asesoria = Asesoria("Consultoria", 100_000, "senior")


class TestReservaCreacion(TestReservaSetUp):
    """Verifica el estado inicial de una reserva al crearse."""

    def test_estado_inicial_es_pendiente(self):
        r = Reserva(self.cliente, self.sala, 2.0)
        self.assertEqual(r.estado, EstadoReserva.PENDIENTE)

    def test_costo_calculado_correctamente_con_iva(self):
        # 2 horas a $60000 + 19% IVA = $142800
        r = Reserva(self.cliente, self.sala, 2.0)
        self.assertAlmostEqual(r.costo, 60_000 * 2 * 1.19, places=1)

    def test_costo_con_descuento_es_menor(self):
        r_sin = Reserva(self.cliente, self.sala, 2.0)
        r_con = Reserva(self.cliente, self.sala, 2.0, descuento=0.10)
        self.assertLess(r_con.costo, r_sin.costo)

    def test_cantidad_negativa_lanza_error(self):
        with self.assertRaises(ValorNegativoError):
            Reserva(self.cliente, self.sala, -1.0)

    def test_descuento_mayor_a_uno_lanza_error(self):
        with self.assertRaises(ValorNegativoError):
            Reserva(self.cliente, self.sala, 2.0, descuento=1.5)

    def test_cliente_invalido_lanza_error(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva("no soy cliente", self.sala, 2.0)

    def test_servicio_invalido_lanza_error(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva(self.cliente, "no soy servicio", 2.0)

    def test_id_no_es_vacio(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        self.assertTrue(len(r.id) > 0)

    def test_resumen_tiene_campos_clave(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        d = r.resumen()
        for campo in ["id", "estado", "cliente", "servicio", "costo_total"]:
            self.assertIn(campo, d)


class TestReservaTransicionEstados(TestReservaSetUp):
    """Verifica las transiciones válidas e inválidas de estado."""

    def test_confirmar_desde_pendiente_funciona(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        r.confirmar()
        self.assertEqual(r.estado, EstadoReserva.CONFIRMADA)

    def test_confirmar_dos_veces_lanza_error(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        r.confirmar()
        with self.assertRaises(EstadoReservaError):
            r.confirmar()

    def test_cancelar_desde_pendiente_funciona(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        r.cancelar("Test")
        self.assertEqual(r.estado, EstadoReserva.CANCELADA)

    def test_cancelar_desde_confirmada_funciona(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        r.confirmar()
        r.cancelar("Cambio de planes")
        self.assertEqual(r.estado, EstadoReserva.CANCELADA)

    def test_cancelar_dos_veces_lanza_error(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        r.cancelar("Primera vez")
        with self.assertRaises(EstadoReservaError):
            r.cancelar("Segunda vez")

    def test_fecha_confirmacion_se_asigna_al_confirmar(self):
        r = Reserva(self.cliente, self.sala, 1.0)
        self.assertIsNone(r.fecha_confirmacion)
        r.confirmar()
        self.assertIsNotNone(r.fecha_confirmacion)


class TestReservaServicioDesactivado(TestReservaSetUp):
    """Verifica que no se puede reservar un servicio inactivo."""

    def test_servicio_desactivado_lanza_error(self):
        self.sala.desactivar()
        with self.assertRaises(ReservaInvalidaError):
            Reserva(self.cliente, self.sala, 2.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
