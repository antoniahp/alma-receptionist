# Alma

**Alma** es una app para centros de estética pequeños en la que **las citas mueven todo lo demás**:

- **Agenda y reservas online.** Solo se ofrecen huecos donde cabe el servicio entero y nunca se reserva dos veces la misma hora.
- **Recepcionista por Telegram y en la web.** Cercana y con el tono del centro. Contesta precios y horarios, recomienda tratamientos y reserva, cambia o anula citas. Funciona con **Gemma en local** (Ollama) y, si la IA no está disponible, con reglas.
- **Cuando no sabe contestar, avisa a la dueña.** La dueña responde desde el panel o desde Telegram, y la respuesta le llega a la clienta en su chat.
- **Recordatorios 24 h antes**, con botones para confirmar o cambiar la cita.
- **Avisos para repetir** cuando a una clienta le toca volver.
- **Inventario que se pide solo.** Cada servicio gasta producto, la previsión cruza el stock con las reservas y la IA redacta el pedido al proveedor. La dueña lo aprueba con un botón.

**Stack:** Python 3.12, Django 5.2, Django REST Framework, PostgreSQL, Poetry y pytest en el backend; React y Vite en el frontend; Telegram Bot API; Ollama con Gemma; Docker Compose y Render para el despliegue.

---

## Arquitectura

El backend sigue una **arquitectura hexagonal** con **CQRS** en la capa de aplicación. Las dependencias siempre apuntan hacia dentro: la infraestructura conoce la aplicación, la aplicación conoce el dominio y el dominio no conoce a nadie.

```
backend/
├── core/                        Configuración de Django (settings, urls, wsgi)
├── domain/                      DOMINIO: no sabe nada de la API, Telegram ni la IA
│   ├── entities/                Un fichero por entidad: modelos de Django (id UUID4) y objetos que no se guardan
│   ├── repositories/            Interfaces de acceso a datos (AppointmentRepository, ClientRepository...)
│   ├── services/                Interfaces de servicios externos (MessageService, LanguageModelService, EmailService)
│   ├── rules/                   Reglas puras: huecos libres, previsión de stock, textos para clientas...
│   ├── exceptions.py            Errores de negocio (SlotNotAvailable, OrderNotDraft...)
│   └── models.py                Solo reexporta las entidades (Django busca aquí los modelos)
├── application/                 APLICACIÓN (CQRS)
│   ├── commands/<accion>/       command.py + command_dto.py   → cambian datos
│   ├── queries/<consulta>/      query.py + query_dto.py       → solo leen
│   └── shared/                  Piezas que comparten varios commands (la recepcionista)
├── infrastructure/              INFRAESTRUCTURA
│   ├── api/<vista>/             view.py + serializer.py (un directorio por vista)
│   ├── urls.py                  Todas las rutas de la API
│   ├── repositories/            Implementación de los repositorios con el ORM de Django
│   ├── services/                Telegram, Ollama y correo (implementan los servicios del dominio)
│   ├── dependencies.py          Qué implementación real usa cada repositorio y servicio
│   ├── telegram_bot/            Convierte cada mensaje de Telegram en un command
│   ├── management/commands/     run_bot, send_notifications, seed_demo, ensure_owner
│   └── admin.py
└── tests/                       La misma estructura: domain/, application/, infrastructure/
```

La capa de aplicación nunca usa el ORM: todo acceso a datos pasa por un **repositorio**, y todo lo externo por un **servicio**. Cada command o query los recibe en el constructor:

```python
# application/commands/book_appointment/command_dto.py
@dataclass(frozen=True)
class BookAppointmentCommandDTO:
    client_id: UUID
    service_id: UUID
    start: datetime
    source: str

# infrastructure/api/appointments/view.py
appointment = BookAppointmentCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
    BookAppointmentCommandDTO(client_id=..., service_id=..., start=..., source=Appointment.SOURCE_OWNER)
)
```

`Repositories` agrupa todos los repositorios en un solo objeto (`repositories.appointments`, `repositories.clients`...), para no pasar nueve parámetros.

**Reglas que protegen al negocio:**
- **Reservas.** Se bloquea el horario del día con `select_for_update` dentro de una transacción. Dos reservas a la vez nunca cogen el mismo hueco.
- **Estados.** Una cita completada, cancelada o no presentada no se puede volver a completar ni cancelar. El stock nunca se descuenta dos veces.
- **Pedidos.** Solo se envía o descarta un borrador, y solo se recibe un pedido enviado.
- **IA.** Las acciones que propone se validan antes de ejecutarse. Si dice "te he reservado" sin haberlo hecho, se corrige con botones reales.
- **Errores.** Los errores de negocio llegan al frontend con un mensaje claro (400, 404 o 409), nunca como un 500.

---

## Puesta en marcha en local

### Opción A: Docker Compose (lo más rápido)

```bash
cp backend/.env.example backend/.env
docker compose up --build
docker compose exec backend python manage.py seed_demo   # datos de ejemplo + usuario cris / alma1234
```

- **Web del centro** (lo que ven las clientas: tratamientos, reserva y chat con Aura): http://localhost:5173
- **Panel de la dueña** (citas, mensajes, recordatorios y productos): http://localhost:5173/panel
- Admin: http://localhost:8000/admin

Para arrancar también el bot de Telegram: `docker compose --profile telegram up`.

### Opción B: sin Docker

```bash
cd backend
python -m poetry install
cp .env.example .env
poetry run python manage.py migrate
poetry run python manage.py seed_demo
poetry run python manage.py runserver
```

Y en otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Sin `DATABASE_URL`, el backend usa SQLite en local. Con Docker y en Render usa PostgreSQL.

### IA local (Gemma)

1. Instala Ollama: https://ollama.com
2. Descarga el modelo: `ollama pull gemma3:4b`
3. Déjalo abierto. Docker Compose ya apunta a `host.docker.internal:11434`.

Sin Ollama la app funciona igual: la recepcionista responde con reglas y los pedidos usan una plantilla.

### Bot de Telegram

1. Crea el bot con **@BotFather** y copia el token.
2. En `backend/.env`, rellena `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME` (sin @) y `TELEGRAM_OWNER_CHAT_ID`. Este último es el chat de la dueña, para los avisos; se consulta con @userinfobot.
3. Arranca el bot con `poetry run python manage.py run_bot` (o con el perfil `telegram` de Compose). Atiende los mensajes y, cada minuto, envía los recordatorios y los avisos para repetir.

### Comparador de precios (SerpApi)

En **Productos**, cada producto tiene un botón *Comparar precios*. Busca el producto en Google Shopping a través de [SerpApi](https://serpapi.com/google-shopping-api) y enseña las tiendas ordenadas de más barata a más cara, con lo que te ahorrarías frente a lo que pagas ahora.

1. Crea una cuenta en serpapi.com (el plan gratuito da 100 búsquedas al mes).
2. Pon la clave en `backend/.env`: `SERPAPI_API_KEY=...`
3. Reinicia el backend.

Cada clic es una búsqueda: solo se busca cuando la dueña lo pide, nunca de forma automática.

---

## Tests

```bash
cd backend
poetry run pytest
```

Se usa **pytest**, **pytest-django** y **model_bakery**. Los repositorios son los reales de Django contra una base de datos de test. Telegram, la IA y el correo se sustituyen por versiones falsas (`tests/fakes.py`), así que los tests no necesitan red. El estilo se revisa con **ruff** (`poetry run ruff check .` y `poetry run ruff format .`). Pasan igual con SQLite y con PostgreSQL:

```bash
DATABASE_URL=postgres://usuario@localhost:5432/base poetry run pytest
```

---

## Despliegue en Render

El fichero `render.yaml` es un *Blueprint*. En Render, ve a **New → Blueprint** y elige el repositorio. Se crea:

| Servicio | Tipo | Plan |
|---|---|---|
| `alma-db` | PostgreSQL | free |
| `alma-backend` | Web (Docker) | free |
| `alma-frontend` | Static site | free |
| `alma-telegram-bot` | Background worker | starter (de pago: los workers no tienen plan gratuito) |

Render te pide estas variables:
- **Backend:** `CORS_ALLOWED_ORIGINS` (la URL del frontend), `CSRF_TRUSTED_ORIGINS` (la URL del backend), `OWNER_USERNAME` y `OWNER_PASSWORD` (el usuario del panel se crea solo al arrancar).
- **Frontend:** `VITE_API_URL`, la URL del backend sin barra final.
- **Comunes** (grupo `alma-settings`): datos del negocio y de Telegram.

A tener en cuenta:
- La IA local **no** corre en Render. `LLM_ENABLED` está en `false`, o puedes apuntar `OLLAMA_URL` a un servidor con Ollama.
- El plan gratuito de Render duerme el backend tras unos minutos sin uso y la base de datos gratuita caduca a los 30 días. Para el negocio real conviene un plan de pago.
- **Dominio propio (.tech):** en cada servicio de Render, *Settings → Custom Domains*. Por ejemplo, `app.tudominio.tech` para el frontend y `api.tudominio.tech` para el backend. En tu proveedor del dominio crea un registro CNAME para cada uno apuntando a la dirección `.onrender.com` que te da Render. Después actualiza `VITE_API_URL=https://api.tudominio.tech`, `CORS_ALLOWED_ORIGINS=https://app.tudominio.tech` y `CSRF_TRUSTED_ORIGINS=https://api.tudominio.tech`.
- Si no despliegas el bot, los recordatorios se pueden enviar con un Cron Job de Render que ejecute `python manage.py send_notifications`.

---

## White label

El nombre del negocio, la dueña, la dirección y la asistente vienen de variables de entorno. Los servicios, productos, consumos, horarios y palabras clave se editan en el admin. Con eso, la misma app sirve para otro centro, una peluquería o un estudio de uñas.
