# Sistema de Reservas v2.0 — Software FJ

> Proyecto académico universitario — UNAD
> Python · POO avanzada · Patrones de diseño · Testing con unittest · Clean Code

---

## Descripción del sistema

Software FJ gestiona clientes, servicios y reservas sin base de datos — todo vive en objetos Python. La versión 2.0 incorpora tres patrones de diseño clásicos (Factory, Observer, Strategy), un motor de facturación automática, exportación a CSV, búsqueda avanzada y una suite de pruebas unitarias con unittest.

El principio rector fue construir código que se pueda cambiar sin miedo: agregar un nuevo tipo de servicio, una nueva estrategia de descuento o un nuevo canal de notificación no requiere tocar las clases existentes.

---

## Arquitectura del proyecto

```

sistema-reservas-poo/
│
├── src/
│   ├── main.py
│   ├── models/
│   │   ├── cliente.py          ← Encapsulación fuerte, regex de validación
│   │   ├── servicio.py         ← Clase abstracta + ReservaSala, AlquilerEquipo, Asesoria
│   │   ├── reserva.py          ← Ciclo PENDIENTE → CONFIRMADA → CANCELADA
│   │   └── factura.py          ← Generada al confirmar (dataclass + contador correlativo)
│   ├── services/
│   │   └── gestion_reservas.py ← Fachada v2.0: Observable + Context Manager
│   ├── patterns/
│   │   ├── factory.py          ← ServicioFactory (Factory Method)
│   │   ├── observer.py         ← Observable, NotificadorCorreo, RegistroAuditoria
│   │   └── strategy.py         ← EstrategiaDescuento + 4 implementaciones concretas
│   ├── exceptions/
│   │   └── custom_exceptions.py ← Jerarquía de 8 excepciones personalizadas
│   └── utils/
│       ├── logger.py            ← Logger centralizado → logs/app.log
│       └── exportador.py        ← ExportadorCSV + BuscadorReservas
├── logs/
│   └── app.log
├── tests/
│   ├── simulacion.py            ← 12 operaciones demostrativas
│   ├── test_cliente.py          ← 13 pruebas unitarias de Cliente
│   ├── test_reserva.py          ← 11 pruebas de estados y validaciones
│   └── test_gestion.py          ← 12 pruebas de integración + patrones
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Patrones de diseño implementados

**Factory Method** — La clase `ServicioFactory` crea instancias a partir de un string de tipo. El código cliente nunca llama a los constructores directamente. Agregar un cuarto tipo de servicio solo requiere modificar la fábrica, no los puntos de uso.

**Observer** — `GestionReservas` hereda de `Observable` y emite eventos como `reserva_confirmada` o `reserva_cancelada`. Tres observadores concretos disponibles: `NotificadorCorreo` (simula correo), `NotificadorFacturacion` y `RegistroAuditoria`. Suscribir o desuscribir es una línea de código.

**Strategy** — Cinco estrategias de descuento intercambiables: `SinDescuento`, `DescuentoClienteVIP` (20% fijo), `DescuentoVolumen` (escalonado), `DescuentoTemporadaBaja` (15% ene-mar) y `DescuentoCombinado`. Todas implementan la interfaz abstracta `EstrategiaDescuento`.

---

## Cómo ejecutar

```bash
# Clonar
git clone https://github.com/clr-techlead/AC-3---Fase-4---Componente-pr-ctico---Pr-cticas-simuladas---UNAD.git

# Demo principal
python src/main.py

# Simulación con 12 operaciones
python tests/simulacion.py

# Tests unitarios (individual)
python -m unittest tests/test_cliente.py -v
python -m unittest tests/test_reserva.py -v
python -m unittest tests/test_gestion.py -v

# Todos los tests
python -m unittest discover tests -v
```

---

## Ejemplos de uso

### Context Manager

```python
with GestionReservas() as sistema:
    c = sistema.registrar_cliente('Ana', 'ana@ok.com', '3001234567')
    sala = ServicioFactory.crear('sala', 'Sala Norte', 80_000, capacidad=15)
    sistema.registrar_servicio(sala)
    r = sistema.crear_reserva(c.id, sala.id, 3.0)
    sistema.confirmar_reserva(r.id)  # genera factura automáticamente
```

### Observadores

```python
sistema = GestionReservas()
sistema.suscribir(NotificadorCorreo())
sistema.suscribir(RegistroAuditoria())
# cada evento posterior notifica a ambos
```

### Estrategia de descuento

```python
estrategia = DescuentoClienteVIP()
precio_final = estrategia.aplicar(200_000, cantidad=1)
# → 160_000 (20% descuento)
```

### Exportar a CSV

```python
exp = ExportadorCSV('exports')
ruta = exp.exportar_reservas(sistema.listar_reservas())
```

### Búsqueda avanzada

```python
buscador = BuscadorReservas(sistema.listar_reservas())
confirmadas = buscador.por_estado('CONFIRMADA')
caras = buscador.por_costo_minimo(200_000)
ordenadas = buscador.ordenar_por_costo(ascendente=False)
```

---

## Manejo de excepciones

| Situación | Excepción | Respuesta |
|---|---|---|
| Email inválido o vacío | `ClienteInvalidoError` / `CampoVacioError` | Retorna `None` |
| Servicio inexistente | `ServicioNoEncontradoError` | Reserva rechazada |
| Reserva duplicada | `ReservaDuplicadaError` | Retorna `None` |
| Estado inválido | `EstadoReservaError` | Retorna `False` |
| Valor negativo | `ValorNegativoError` | Retorna `None` |
| Error de cálculo | `CalculoCostoError` | Retorna `None` |

Bloques usados: `try/except`, `try/except/else`, `try/except/finally`, encadenamiento con `raise ... from exc`.

---

## Suite de tests

| Archivo | Tests | Qué verifica |
|---|---|---|
| test_cliente.py | 13 | Creación, validaciones, getters, igualdad |
| test_reserva.py | 11 | Estados, costos, descuentos, servicio inactivo |
| test_gestion.py | 12 | Flujo completo, context manager, Factory, Observer, Strategy |

```
python -m unittest discover tests -v
# Ran 36 tests in ~0.1s
# OK
```

---

## Conceptos POO aplicados

**Abstracción:** `Servicio` y `EstrategiaDescuento` son clases abstractas que definen contratos sin implementación concreta.

**Herencia:** Los tres tipos de servicio extienden `Servicio`. `GestionReservas` hereda de `Observable`. Las excepciones forman jerarquía donde `CampoVacioError` especializa `ClienteInvalidoError`.

**Polimorfismo:** `calcular_costo()` se comporta diferente en cada subtipo de servicio. Los observadores reciben el mismo `actualizar()` pero reaccionan de forma independiente.

**Encapsulación:** Todos los atributos críticos son privados (`__nombre`, `__estado`, etc.). El acceso pasa por properties con validación.

**Dataclasses:** `LineaFactura` usa `@dataclass` donde no hay lógica de validación compleja.

**Context Manager:** `GestionReservas` implementa `__enter__`/`__exit__` para garantizar cierre limpio del contexto.
