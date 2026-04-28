# Python OOP Reservation System

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![OOP](https://img.shields.io/badge/Paradigm-Object--Oriented-blue?style=flat-square)]()
[![Design Patterns](https://img.shields.io/badge/Design%20Patterns-Factory%20%7C%20Observer%20%7C%20Strategy-green?style=flat-square)]()
[![Tests](https://img.shields.io/badge/Tests-36%20unittest-brightgreen?style=flat-square&logo=pytest)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)]()

> A full-featured business reservation management system built with Python, demonstrating advanced Object-Oriented Programming, classic design patterns, automated billing, CSV reporting, and a complete unittest suite.

---

## Overview

This project simulates the internal management platform of a fictional company called **Software FJ**, handling three core business domains: clients, services, and reservations. The entire data layer lives in memory using Python objects — no database required.

The system was architected to be open for extension and closed for modification: adding a new service type, a discount strategy, or a notification channel requires zero changes to existing classes.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Paradigm | Object-Oriented Programming (OOP) |
| Design Patterns | Factory Method, Observer, Strategy |
| Testing | unittest (36 tests) |
| Data Export | CSV (stdlib) |
| Logging | logging module → file + console |
| Dependencies | None (stdlib only) |

---

## Key Features

- **Full reservation lifecycle** — PENDING → CONFIRMED → CANCELLED with state validation
- **Automatic invoice generation** — created on confirmation with sequential numbering
- **3 service types** — Room Booking, Equipment Rental, Professional Advisory
- **5 discount strategies** — Standard, VIP Client (20%), Volume (tiered), Low Season, Combined
- **Observer notifications** — email simulator, billing logger, full audit trail
- **CSV export** — reservations and invoices exportable to spreadsheet
- **Advanced search** — filter by status, client name, date range, minimum cost
- **Context Manager** support for clean resource handling
- **Custom exception hierarchy** — 8 specialized exceptions with chaining
- **Centralized logging** — timestamped entries in `logs/app.log`

---

## Project Architecture

```
python-oop-reservation-system/
│
├── src/
│   ├── main.py                    # Entry point
│   ├── models/
│   │   ├── cliente.py             # Client entity — strong encapsulation + regex validation
│   │   ├── servicio.py            # Abstract base + ReservaSala, AlquilerEquipo, Asesoria
│   │   ├── reserva.py             # Core domain — full lifecycle management
│   │   └── factura.py             # Invoice model — dataclass + auto-counter
│   ├── services/
│   │   └── gestion_reservas.py    # Service layer — Observable + Context Manager
│   ├── patterns/
│   │   ├── factory.py             # Factory Method pattern
│   │   ├── observer.py            # Observer pattern — 3 concrete observers
│   │   └── strategy.py            # Strategy pattern — 5 discount strategies
│   ├── exceptions/
│   │   └── custom_exceptions.py   # Custom exception hierarchy (8 classes)
│   └── utils/
│       ├── logger.py              # Centralized logger
│       └── exportador.py          # CSV exporter + advanced search engine
│
├── tests/
│   ├── simulacion.py              # Live demo — 12 operations
│   ├── test_cliente.py            # 13 unit tests
│   ├── test_reserva.py            # 11 unit tests
│   └── test_gestion.py            # 12 integration tests
│
├── logs/app.log
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/clr-techlead/python-oop-reservation-system.git
cd python-oop-reservation-system

# No dependencies needed — Python 3.10+ is all you need

# Run the main demo
python src/main.py

# Run the full simulation (12 operations including error scenarios)
python tests/simulacion.py

# Run the full test suite
python -m unittest discover tests -v
```

---

## Usage Examples

### Context Manager

```python
from src.services.gestion_reservas import GestionReservas
from src.patterns.factory import ServicioFactory

with GestionReservas() as sistema:
    client = sistema.registrar_cliente('Ana Torres', 'ana@company.com', '3001234567')
    room = ServicioFactory.crear('sala', 'Main Conference Room', 80_000, capacidad=20)
    sistema.registrar_servicio(room)
    booking = sistema.crear_reserva(client.id, room.id, cantidad=3.0)
    sistema.confirmar_reserva(booking.id)  # auto-generates invoice
```

### Observer Pattern

```python
from src.patterns.observer import NotificadorCorreo, RegistroAuditoria

sistema = GestionReservas()
sistema.suscribir(NotificadorCorreo())   # simulates email on every event
sistema.suscribir(RegistroAuditoria())   # full audit trail
```

### Strategy Pattern — Discount pricing

```python
from src.patterns.strategy import DescuentoClienteVIP, DescuentoCombinado, DescuentoVolumen

vip = DescuentoClienteVIP()                  # 20% fixed discount
volume = DescuentoVolumen()                  # tiered: 10% (5+), 20% (10+)
combined = DescuentoCombinado(vip, volume)   # applies the best of both

final_price = combined.aplicar(200_000, cantidad=6)
```

### CSV Export & Advanced Search

```python
from src.utils.exportador import ExportadorCSV, BuscadorReservas

# Export
ExportadorCSV('exports').exportar_reservas(sistema.listar_reservas())

# Search
buscador = BuscadorReservas(sistema.listar_reservas())
results = buscador.busqueda_combinada(estado='CONFIRMED', costo_minimo=150_000)
```

---

## OOP Concepts Demonstrated

| Concept | Implementation |
|---|---|
| **Abstraction** | `Servicio` (ABC), `EstrategiaDescuento` (ABC), `Observador` (ABC) |
| **Inheritance** | 3 service subclasses, exception hierarchy, `GestionReservas` ← `Observable` |
| **Polymorphism** | `calcular_costo()` per service type, `actualizar()` per observer |
| **Encapsulation** | All attributes private (`__name`), access via `@property` with validation |
| **Dataclasses** | `LineaFactura` — clean data container without boilerplate |
| **Context Manager** | `__enter__` / `__exit__` in `GestionReservas` |

---

## Error Handling Strategy

The system **never crashes**. Every public method catches its own exceptions, logs the event, and returns a safe value (`None` or `False`).

| Block Type | Where Used |
|---|---|
| `try / except` | All public methods |
| `try / except / else` | Client registration, reservation creation |
| `try / except / finally` | Service registration, confirmation flow |
| `raise X from Y` | Exception chaining in nested service lookups |

---

## Test Coverage

| File | Tests | Scope |
|---|---|---|
| `test_cliente.py` | 13 | Validation, normalization, equality |
| `test_reserva.py` | 11 | State transitions, cost calculation, edge cases |
| `test_gestion.py` | 12 | Full flow, Factory, Observer, Strategy, Context Manager |
| **Total** | **36** | **All layers covered** |

---

## Author

Developed as a portfolio project demonstrating professional Python development skills.
Applicable to **Full Stack Developer**, **Data Analyst**, and **Software Engineer** roles.

---

## License

MIT — free to use and adapt.
