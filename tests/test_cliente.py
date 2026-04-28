# ==============================================================
# test_cliente.py
# Pruebas unitarias para la clase Cliente
# Cubre: creación válida, validaciones, getters, igualdad
# ==============================================================

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from src.models.cliente import Cliente
from src.exceptions.custom_exceptions import (
    ClienteInvalidoError, CampoVacioError
)


class TestClienteCreacionValida(unittest.TestCase):
    """Verifica que un cliente válido se crea correctamente."""

    def setUp(self):
        self.cliente = Cliente("Ana Torres", "ana@correo.com", "3001234567")

    def test_nombre_se_normaliza_a_title_case(self):
        self.assertEqual(self.cliente.nombre, "Ana Torres")

    def test_email_se_convierte_a_minusculas(self):
        self.assertEqual(self.cliente.email, "ana@correo.com")

    def test_telefono_se_almacena_correctamente(self):
        self.assertEqual(self.cliente.telefono, "3001234567")

    def test_id_no_es_vacio(self):
        self.assertTrue(len(self.cliente.id) > 0)

    def test_id_es_solo_lectura(self):
        with self.assertRaises(AttributeError):
            self.cliente.id = "nuevo_id"

    def test_repr_contiene_datos_clave(self):
        repr_str = repr(self.cliente)
        self.assertIn("Ana Torres", repr_str)
        self.assertIn("ana@correo.com", repr_str)

    def test_to_dict_tiene_claves_correctas(self):
        d = self.cliente.to_dict()
        self.assertIn("id", d)
        self.assertIn("nombre", d)
        self.assertIn("email", d)
        self.assertIn("telefono", d)


class TestClienteValidaciones(unittest.TestCase):
    """Verifica que los setters rechazan datos inválidos."""

    def test_nombre_vacio_lanza_campo_vacio_error(self):
        with self.assertRaises(CampoVacioError):
            Cliente("", "ok@test.com", "3001234567")

    def test_nombre_solo_espacios_lanza_error(self):
        with self.assertRaises(CampoVacioError):
            Cliente("   ", "ok@test.com", "3001234567")

    def test_nombre_demasiado_corto_lanza_error(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("A", "ok@test.com", "3001234567")

    def test_email_invalido_lanza_error(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("Juan", "no-es-email", "3001234567")

    def test_email_vacio_lanza_error(self):
        with self.assertRaises(CampoVacioError):
            Cliente("Juan", "", "3001234567")

    def test_telefono_invalido_lanza_error(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("Juan", "juan@ok.com", "abc")

    def test_telefono_vacio_lanza_error(self):
        with self.assertRaises(CampoVacioError):
            Cliente("Juan", "juan@ok.com", "")

    def test_telefono_con_prefijo_internacional_es_valido(self):
        """Un teléfono con + debe ser aceptado."""
        c = Cliente("Maria", "maria@ok.com", "+573001234567")
        self.assertIn("+573001234567", c.telefono)


class TestClienteIgualdad(unittest.TestCase):
    """Verifica la identidad de clientes por ID."""

    def test_mismo_objeto_es_igual_a_si_mismo(self):
        c = Cliente("Pedro", "pedro@ok.com", "3001111111")
        self.assertEqual(c, c)

    def test_dos_objetos_distintos_no_son_iguales(self):
        c1 = Cliente("Pedro", "pedro1@ok.com", "3001111111")
        c2 = Cliente("Pedro", "pedro2@ok.com", "3001111111")
        self.assertNotEqual(c1, c2)

    def test_comparar_con_no_cliente_retorna_false(self):
        c = Cliente("Pedro", "pedro@ok.com", "3001111111")
        self.assertNotEqual(c, "no soy un cliente")


if __name__ == "__main__":
    unittest.main(verbosity=2)
