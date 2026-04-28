# Sistema de Reservas — Software FJ

> Proyecto académico de nivel universitario — UNAD
> Programación Orientada a Objetos en Python · Manejo avanzado de excepciones · Diseño limpio

---

## Descripción del sistema

Software FJ necesitaba una plataforma interna para administrar tres recursos clave: sus clientes, el catálogo de servicios que ofrece y las reservas que vinculan a ambos. El sistema resultante es completamente en memoria (sin base de datos), está escrito en Python puro con orientación a objetos y es capaz de seguir operando ante cualquier tipo de error gracias a una capa de manejo de excepciones diseñada cuidadosamente.

El foco técnico del proyecto está en demostrar que el código puede ser limpio, expresivo y robusto al mismo tiempo, sin sacrificar ninguno de esos tres atributos.

---

## Arquitectura del proyecto

```
sistema-reservas-poo/
│
├── src/
│   ├── main.py                        ← Punto de entrada
│   │
│   ├── models/
│   │   ├── cliente.py                 ← Clase Cliente (encapsulación fuerte)
│   │   ├── servicio.py                ← Clase abstracta + ReservaSala, AlquilerEquipo, Asesoria
│   │   └── reserva.py                 ← Núcleo del sistema (ciclo de vida completo)
│   │
│   ├── services/
│   │   └── gestion_reservas.py        ← Fachada de negocio (orquesta todo)
│   │
│   ├── exceptions/
│   │   └── custom_exceptions.py       ← Jerarquía de excepciones personalizadas
│   │
│   └── utils/
│       └── logger.py                  ← Logger centralizado → logs/app.log
│
├── logs/
│   └── app.log                        ← Generado en tiempo de ejecución
│
├── tests/
│   └── simulacion.py                  ← 12 operaciones: éxitos + errores
│
├── README.md
├── requirements.txt
└── .gitignore
```

### Por qué esta estructura

Cada carpeta tiene una responsabilidad única. Los modelos son solo datos + reglas de dominio. Los servicios son operaciones de negocio. Las excepciones son su propio módulo para que puedan importarse desde cualquier lado sin generar dependencias circulares. El logger es un singleton funcional disponible con un simple `from src.utils.logger import log`.

---

## Cómo ejecutar el proyecto

### Requisitos previos

- Python 3.10 o superior
- No se necesitan librerías externas

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/clr-techlead/AC-3---Fase-4---Componente-pr-ctico---Pr-cticas-simuladas---UNAD.git
cd AC-3---Fase-4---Componente-pr-ctico---Pr-cticas-simuladas---UNAD

# 2. Ejecutar el punto de entrada
python src/main.py

# 3. Ejecutar la simulación completa (recomendado para ver el manejo de errores)
python tests/simulacion.py
```

Después de ejecutar, el archivo `logs/app.log` contendrá el historial detallado de todas las operaciones.

---

## Ejemplos de uso

### Registrar un cliente

```python
from src.services.gestion_reservas import GestionReservas

sistema = GestionReservas()
cliente = sistema.registrar_cliente(
    nombre="Ana Torres",
    email="ana@correo.com",
    telefono="3001234567"
)
print(cliente)  # Cliente(id='A1B2C3D4', nombre='Ana Torres', ...)
```

### Crear y confirmar una reserva

```python
from src.models.servicio import ReservaSala

sala = ReservaSala("Sala Norte", precio_por_hora=80_000, capacidad=20)
sistema.registrar_servicio(sala)

reserva = sistema.crear_reserva(cliente.id, sala.id, cantidad=3.0)
sistema.confirmar_reserva(reserva.id)
print(f"Costo: {reserva.costo:,.2f} COP")
```

### Calcular costo con descuento

```python
# 10% de descuento + IVA incluido
reserva = sistema.crear_reserva(
    cliente.id, sala.id, cantidad=2.0, descuento=0.10
)
```

---

## Manejo de errores

El sistema nunca se detiene. Cada operación pública en `GestionReservas` atrapa sus propios errores, los registra y retorna un valor seguro (`None` o `False`).

| Situación | Excepción lanzada | Respuesta del sistema |
|---|---|---|
| Email inválido | `ClienteInvalidoError` | Retorna `None`, registra en log |
| Campo vacío | `CampoVacioError` | Retorna `None`, registra en log |
| Servicio no existe | `ServicioNoEncontradoError` | Reserva rechazada |
| Reserva duplicada | `ReservaDuplicadaError` | Retorna `None` |
| Confirmar ya confirmada | `EstadoReservaError` | Retorna `False` |
| Valor negativo | `ValorNegativoError` | Retorna `None` |
| Error de cálculo | `CalculoCostoError` | Retorna `None` |

Todos los eventos quedan en `logs/app.log` con timestamp, nivel y descripción.

---

## Conceptos POO aplicados

**Abstracción:** `Servicio` es una clase abstracta (ABC) que define el contrato `calcular_costo()` y `descripcion()`. Ninguna instancia directa es posible; solo las subclases concretas.

**Herencia:** `ReservaSala`, `AlquilerEquipo` y `Asesoria` extienden `Servicio` y especializan tanto el cálculo de costo como la descripción.

**Polimorfismo:** El método `calcular_costo_con_iva()` de la clase base llama internamente a `calcular_costo()`, que en tiempo de ejecución resuelve a la versión correcta según el tipo concreto del objeto.

**Encapsulación:** Todos los atributos de `Cliente`, `Servicio` y `Reserva` son privados (doble guión bajo). El acceso externo se hace exclusivamente mediante `@property` y setters que validan cada valor antes de asignarlo.

---

## Robustez del sistema

- `try / except` en cada operación pública
- `try / except / else` para separar flujo exitoso del de error
- `try / except / finally` para garantizar logs incluso cuando falla algo
- Encadenamiento de excepciones con `raise ... from exc` para no perder el contexto original
- Jerarquía de excepciones propia: `ErrorBase` → `ClienteInvalidoError` → `CampoVacioError`

---

## Resultado de la simulación

Al ejecutar `tests/simulacion.py` se procesan 12 operaciones: registro de servicios y clientes válidos, intentos con datos incorrectos, reservas exitosas, detección de duplicados, confirmación, cancelación e intento de confirmar un estado ya cerrado. El sistema completa las 12 operaciones sin lanzar ninguna excepción no controlada.
