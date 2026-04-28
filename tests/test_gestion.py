# ==============================================================
# test_gestion.py
# Pruebas de integración para GestionReservas
# Cubre: flujo completo, context manager, búsquedas
# ==============================================================

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from src.services.gestion_reservas import GestionReservas
from src.models.servicio import ReservaSala, AlquilerEquipo
from src.models.reserva import EstadoReserva
from src.patterns.factory import ServicioFactory
from src.patterns.observer import NotificadorCorreo, RegistroAuditoria
from src.patterns.strategy import DescuentoClienteVIP, DescuentoVolumen


class TestGestionReservasBase(unittest.TestCase):
    """setUp común para todos los tests de integración."""

    def setUp(self):
        self.sistema = GestionReservas()
        self.sala = ReservaSala("Sala Principal", 80_000, 20)
        self.equipo = AlquilerEquipo("Proyector HD", 25_000, False)
        self.sistema.registrar_servicio(self.sala)
        self.sistema.registrar_servicio(self.equipo)
        self.c1 = self.sistema.registrar_cliente(
            "Carlos López", "carlos@ok.com", "3001111111"
        )
        self.c2 = self.sistema.registrar_cliente(
            "Sofia Mendez", "sofia@ok.com", "3002222222"
        )


class TestFlujoCompleto(TestGestionReservasBase):
    """Prueba el ciclo completo: crear → confirmar → reporte."""

    def test_crear_reserva_exitosa_retorna_objeto(self):
        r = self.sistema.crear_reserva(self.c1.id, self.sala.id, 2.0)
        self.assertIsNotNone(r)

    def test_confirmar_reserva_cambia_estado(self):
        r = self.sistema.crear_reserva(self.c1.id, self.sala.id, 2.0)
        self.sistema.confirmar_reserva(r.id)
        self.assertEqual(r.estado, EstadoReserva.CONFIRMADA)

    def test_cancelar_reserva_cambia_estado(self):
        r = self.sistema.crear_reserva(self.c1.id, self.sala.id, 2.0)
        ok = self.sistema.cancelar_reserva(r.id, "Prueba")
        self.assertTrue(ok)
        self.assertEqual(r.estado, EstadoReserva.CANCELADA)

    def test_reserva_duplicada_retorna_none(self):
        self.sistema.crear_reserva(self.c1.id, self.sala.id, 2.0)
        r2 = self.sistema.crear_reserva(self.c1.id, self.sala.id, 1.0)
        self.assertIsNone(r2)

    def test_cliente_invalido_retorna_none(self):
        r = self.sistema.crear_reserva("ID_INEXISTENTE", self.sala.id, 2.0)
        self.assertIsNone(r)

    def test_reporte_tiene_campos_correctos(self):
        reporte = self.sistema.reporte_general()
        campos = ["clientes_registrados", "servicios_activos",
                  "reservas_confirmadas", "ingresos_confirmados"]
        for c in campos:
            self.assertIn(c, reporte)

    def test_reporte_cuenta_clientes_correctamente(self):
        self.assertEqual(self.sistema.reporte_general()["clientes_registrados"], 2)


class TestContextManager(TestGestionReservasBase):
    """Verifica que GestionReservas funciona como context manager."""

    def test_context_manager_entra_y_sale_sin_error(self):
        try:
            with self.sistema as s:
                r = s.crear_reserva(self.c1.id, self.sala.id, 1.0)
                self.assertIsNotNone(r)
        except Exception as exc:
            self.fail(f"Context manager lanzó excepción inesperada: {exc}")


class TestFactory(unittest.TestCase):
    """Verifica el patrón Factory para creación de servicios."""

    def test_factory_crea_sala_correctamente(self):
        s = ServicioFactory.crear("sala", "Sala Test", 50_000, capacidad=10)
        self.assertEqual(s.nombre, "Sala Test")

    def test_factory_crea_equipo_correctamente(self):
        s = ServicioFactory.crear("equipo", "Laptop Test", 30_000)
        self.assertIsInstance(s, AlquilerEquipo)

    def test_factory_tipo_invalido_lanza_error(self):
        from src.exceptions.custom_exceptions import ServicioNoEncontradoError
        with self.assertRaises(ServicioNoEncontradoError):
            ServicioFactory.crear("tipo_inexistente", "X", 1000)


class TestObserver(TestGestionReservasBase):
    """Verifica que los observadores se notifican correctamente."""

    def test_auditoria_registra_eventos(self):
        auditoria = RegistroAuditoria()
        self.sistema.suscribir(auditoria)
        r = self.sistema.crear_reserva(self.c1.id, self.sala.id, 2.0)
        self.sistema.confirmar_reserva(r.id)
        historial = auditoria.obtener_historial()
        self.assertGreater(len(historial), 0)

    def test_historial_contiene_evento_confirmacion(self):
        auditoria = RegistroAuditoria()
        self.sistema.suscribir(auditoria)
        r = self.sistema.crear_reserva(self.c1.id, self.sala.id, 2.0)
        self.sistema.confirmar_reserva(r.id)
        eventos = [e["evento"] for e in auditoria.obtener_historial()]
        self.assertIn("reserva_confirmada", eventos)


class TestStrategy(unittest.TestCase):
    """Verifica que las estrategias de descuento calculan correctamente."""

    def test_descuento_vip_aplica_20_porciento(self):
        est = DescuentoClienteVIP()
        precio_con = est.aplicar(100_000, 1)
        self.assertAlmostEqual(precio_con, 80_000, places=0)

    def test_descuento_volumen_bajo_5_es_cero(self):
        est = DescuentoVolumen()
        factor = est.calcular_factor(100_000, 3)
        self.assertEqual(factor, 0.0)

    def test_descuento_volumen_10_o_mas_es_20_porciento(self):
        est = DescuentoVolumen()
        factor = est.calcular_factor(100_000, 10)
        self.assertEqual(factor, 0.20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
