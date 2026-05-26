# 🦉 Glosario de Python para Desarrolladores de JavaScript/TypeScript

¡Bienvenido al mundo de Python! Si vienes de trabajar con **React, Next.js, Express, NestJS y pnpm**, muchas cosas te resultarán familiares, pero con nombres y filosofías distintas. Este documento está diseñado para ser tu mapa de ruta, traduciendo los conceptos de Python y las herramientas de este proyecto al ecosistema de JavaScript que ya dominas.

---

## 🗺️ Tabla de Equivalencias Rápidas

| Concepto en JavaScript/TS | Equivalente en Python (Este Proyecto) | ¿Qué es en pocas palabras? |
| :--- | :--- | :--- |
| **Node.js / Bun / Deno** | Python (3.14+) | El entorno de ejecución (Runtime). |
| **pnpm / npm / yarn** | **UV** | El gestor de paquetes y de entornos más rápido. |
| `package.json` | `pyproject.toml` | Archivo de configuración del proyecto y dependencias. |
| `pnpm-workspace.yaml` | `[tool.uv.workspace]` en `pyproject.toml` | Definición de monorepositorio (Workspaces). |
| `node_modules/` | `.venv/` (Virtual Environment) | Carpeta local donde se instalan las dependencias. |
| **Express.js** | **Flask** | Micro-framework web minimalista para APIs. |
| **NestJS (Arquitectura)** | Capas: Route → Service → Repository | Patrón de arquitectura limpia e inyección conceptual. |
| **Zod / class-validator** | **Pydantic** | Validación de esquemas y tipado estático/dinámico. |
| **Prisma / TypeORM** | **SQLAlchemy 2.x** | El ORM para interactuar con la base de datos (Postgres). |
| **dotenv / nestjs/config** | **pydantic-settings** | Carga y validación estricta de variables de entorno (`.env`). |
| **node-cron / BullMQ** | **APScheduler** | Planificador de tareas en segundo plano (Cron jobs). |
| **Telegraf** | **python-telegram-bot** | Framework/Librería para interactuar con la API de Telegram. |
| **Axios / Fetch API** | **HTTPX** | Cliente HTTP moderno, rápido y asíncrono. |
| **Prisma Migrate / Knex** | **Alembic** | Herramienta para gestionar migraciones de base de datos SQL. |

---

## ⚡ 1. UV: El "pnpm" ultra-rápido de Python

En el ecosistema clásico de Python, se usaban múltiples herramientas fragmentadas: `pip` para instalar paquetes, `virtualenv` para aislar proyectos, `poetry` o `pipenv` para gestionar dependencias. **UV** (creado por Astral) llegó para unificar todo esto en una sola herramienta escrita en Rust, siendo increíblemente rápida (tal como `pnpm` o `Bun`).

### 📦 El concepto de Entorno Virtual (`.venv`) vs `node_modules`
En JavaScript, `pnpm install` descarga los paquetes dentro de `node_modules` en la raíz del proyecto.
En Python, para evitar conflictos globales de dependencias entre proyectos, se crea un **Entorno Virtual** (normalmente una carpeta llamada `.venv`). Esta carpeta contiene una copia aislada del ejecutable de Python y sus librerías asociadas. 

> [!IMPORTANT]
> Nunca debes instalar dependencias de Python de forma global. UV se encarga de crear y activar el `.venv` de forma transparente por ti.

### 🔄 Comparativa de comandos: pnpm vs uv

| Acción | En JS (`pnpm`) | En Python (`uv`) |
| :--- | :--- | :--- |
| **Inicializar proyecto** | `pnpm init` | `uv init` |
| **Instalar todo** | `pnpm install` | `uv sync` |
| **Añadir dependencia** | `pnpm add httpx` | `uv add httpx` |
| **Añadir dep. desarrollo**| `pnpm add -D pytest` | `uv add --dev pytest` |
| **Ejecutar script local** | `pnpm dev` / `node script.js` | `uv run python script.py` |
| **Ejecutar comando CLI** | `pnpx prisma db push` | `uv run <comando>` |

### 📁 UV Workspaces (Monorepos)
Al igual que los workspaces de `pnpm`, UV soporta monorepositorios estructurados. En este proyecto tenemos:
- `apps/bot/` (Paquete del Bot de Telegram)
- `apps/server/` (Paquete de la API Flask)
- `packages/shared/` (Código compartido: proveedores de scraping)

> [!WARNING]
> **Quirk de este repositorio:**
> El `pyproject.toml` raíz está vacío a nivel de dependencias de ejecución. Para sincronizar correctamente todas las dependencias de los sub-proyectos (workspaces) y que estén disponibles en el entorno virtual, **siempre debes ejecutar**:
> ```bash
> uv sync --all-packages
> ```
> Esto equivale a hacer un `pnpm install` recursivo en todo el monorepo.

---

## 🛡️ 2. Pydantic: El "Zod" de Python

En JavaScript/TypeScript, usas **Zod** para validar datos provenientes de peticiones HTTP o variables de entorno en tiempo de ejecución. En Python, la herramienta estándar de la industria para esto es **Pydantic**.

### 🧩 Comparación de sintaxis: Zod vs Pydantic

Imagina que quieres validar la información de un usuario:

#### En TypeScript con Zod:
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.number(),
  username: z.string(),
  email: z.string().email(),
  isActive: z.boolean().default(true),
});

type User = z.infer<typeof UserSchema>;

// Validación
const result = UserSchema.parse({ id: 1, username: "luis", email: "invalid-email" });
```

#### En Python con Pydantic (v2):
```python
from pydantic import BaseModel, EmailStr

class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool = True

# Validación
try:
    user = UserSchema(id=1, username="luis", email="invalid-email")
except ValidationError as e:
    print(e.json())
```

### ⚙️ Validación de Variables de Entorno (`pydantic-settings`)
En lugar de usar un simple `dotenv` y acceder a variables no tipadas a través de `process.env.MY_VAR`, en este proyecto usamos `pydantic-settings`. 
Esto funciona igual que los esquemas de configuración en NestJS (`@nestjs/config` con Joi/Zod): **si falta una variable de entorno requerida en el `.env`, la aplicación lanzará un error inmediatamente al arrancar y no iniciará**, previniendo fallos silenciosos en producción.

---

## 🏛️ 3. Dependencias Clave y su Equivalente en JS

### 🌐 Flask (El "Express.js" de Python)
**Flask** es un micro-framework web. Es sumamente ligero y no impone ninguna estructura de carpetas (igual que Express). 
- En Express creas una app con `const app = express()`, defines rutas con `app.get('/path', callback)` y la levantas.
- En Flask creas una app con `app = Flask(__name__)`, defines rutas mediante decoradores `@app.route('/path')` y retornas diccionarios que automáticamente se transforman a JSON.
- **Blueprints** en Flask equivalen a los **Routers** (`express.Router()`) en Express, permitiendo modularizar las rutas en archivos separados.

### 🗄️ SQLAlchemy (El "Prisma" / "TypeORM" de Python)
Es el ORM más potente de Python. En este proyecto se utiliza la versión moderna (SQLAlchemy 2.x) que utiliza tipado estático avanzado a través de `Mapped` y `mapped_column`.

#### Equivalencia conceptual de definición de modelo:

**En TypeORM (TypeScript):**
```typescript
@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  email: string;
}
```

**En SQLAlchemy 2.x (Python):**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
```

> [!NOTE]
> **Base de Datos y Migraciones:** 
> En este proyecto no existe un sistema de migraciones configurado (como `Alembic`, que es el "Prisma Migrate" o "TypeORM Migrations" de Python). La base de datos es únicamente **PostgreSQL** y se ejecuta localmente mediante Docker Compose (`docker compose up db`).

### ⏰ APScheduler (El "Node-cron" / "BullMQ" de Python)
En Node.js, para ejecutar una función todos los días a las 9:00 AM, usarías `node-cron` o una cola más compleja como `BullMQ`. 
En Python, **APScheduler** (Advanced Python Scheduler) te permite programar tareas recurrentes directamente en el proceso de tu servidor web Flask mediante su `BackgroundScheduler`. Se configura para correr la tarea `daily_price_check` a la hora definida en tu configuración.

### 🤖 Python-Telegram-Bot (El "Telegraf" de Python)
Si has construido bots de Telegram en Node.js, seguramente usaste **Telegraf**. 
`python-telegram-bot` es su equivalente directo y el estándar de oro en Python. Utiliza programación asíncrona (`async/await`) y maneja el ciclo de vida del bot mediante un `ApplicationBuilder`, el cual distribuye los mensajes entrantes a diferentes funciones controladoras (llamadas *handlers*).

### 🌐 HTTPX (El "Axios" o "Fetch API" de Python)
En Node.js usas `axios` o el `fetch` nativo para hacer peticiones HTTP asíncronas a APIs de terceros. 
En Python, el estándar moderno es **HTTPX**. 
- Soporta tanto peticiones síncronas (`httpx.get()`) como asíncronas (`await client.get()`) usando un `AsyncClient`.
- En este proyecto, los proveedores de scraping (`packages/shared/`) usarán HTTPX para consumir APIs externas y descargar información de productos.

#### Ejemplo de llamada asíncrona en JS (Axios):
```javascript
const response = await axios.get('https://api.github.com/users/octocat');
console.log(response.data.name);
```

#### Ejemplo homólogo en Python (HTTPX):
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get('https://api.github.com/users/octocat')
    data = response.json()
    print(data["name"])
```

### 🧬 Flask-Migrate y Alembic (El "Drizzle" de Python)
En el ecosistema Node.js, cuando modificas un modelo/entidad y necesitas reflejar ese cambio en la base de datos de producción (añadir columnas, crear tablas), usas herramientas de migración.
En este proyecto utilizamos **Flask-Migrate**, que es un wrapper de Flask para **Alembic** (la herramienta oficial de migraciones de SQLAlchemy).

#### 🗺️ Tabla de Equivalencias de comandos: Drizzle vs Flask-Migrate

| Acción | Drizzle (Node.js) | Flask-Migrate (Python) | ¿Qué hace? |
| :--- | :--- | :--- | :--- |
| **Inicializar** | Configurar `drizzle.config.ts` | `flask db init` | Crea la carpeta de configuración y el entorno de migraciones (`migrations/`). Solo se ejecuta una vez en la vida del proyecto. |
| **Generar** | `drizzle-kit generate` | `flask db migrate -m "descripción"` | Compara tus modelos de SQLAlchemy ([schema.py](file:///c:/Users/USER/Documents/projects/priceowl/apps/server/src/server/models/schema.py)) con el estado actual de Postgres y genera un archivo `.py` de migración en `migrations/versions/`. |
| **Aplicar** | `drizzle-kit migrate` | `flask db upgrade` | Ejecuta las migraciones pendientes en tu base de datos para crear o alterar las tablas físicas. |
| **Revertir** | Manual / Custom Script | `flask db downgrade` | Revierte la última migración aplicada (vuelve al estado anterior). |
| **Forzar directo** | `drizzle-kit push` | `Base.metadata.create_all(...)` | Sincroniza directamente los modelos sin generar archivos de migración (peligroso en producción, evitado aquí). |
| **Semillas** | `tsx seed.ts` | `flask seed-db` (Nuestro comando custom) | Inserta los registros iniciales una vez que las tablas ya existen en la base de datos. |

> [!IMPORTANT]
> **El problema del Huevo y la Gallina (Startup vs CLI):**
> Al iniciar cualquier comando de `flask db ...`, Flask tiene que levantar la aplicación llamando a `create_app()`. Si dentro del inicio de la app intentamos realizar consultas (`SELECT`) de base de datos como poblar tablas semilla antes de que las tablas existan en Postgres, la app fallará con un error `UndefinedTable`. Por eso, la siembra de base de datos se extrajo a un comando CLI dedicado (`flask seed-db`) que se debe correr manualmente justo después de aplicar las migraciones.

---

## 🏗️ 4. Flujo de Arquitectura (NestJS vs Este Proyecto)

Aunque Flask es un micro-framework como Express, este proyecto sigue una **arquitectura por capas estructurada** inspirada en buenas prácticas de software (muy similar a los principios de inyección y separación de responsabilidades de **NestJS**):

```
Petición HTTP ──> Route (Controller) ──> Service ──> Repository ──> Model (DB)
```

### Reglas estrictas de arquitectura en este servidor:
1. **Routes (Controladores / `@Controller` en Nest):**
   - Reciben la petición HTTP, leen parámetros/body y retornan la respuesta JSON (`jsonify`).
   - **Regla:** Nunca importan los Repositorios directamente. Siempre llaman al Servicio.
2. **Services (Proveedores de lógica / `@Injectable` en Nest):**
   - Contienen las reglas de negocio (ej. "si el precio bajó, notificar al usuario").
   - **Regla:** Son agnósticos de la plataforma web. No importan nada relacionado con Flask (como `request` o `jsonify`).
3. **Repositories (Acceso a datos / `@Injectable` de datos o Custom Repositories):**
   - Contienen únicamente las consultas directas de base de datos usando SQLAlchemy (`db.session.execute(...)`).
   - **Regla:** No contienen lógica de negocio. Solo guardan, actualizan o consultan información.
4. **Models (Entidades / `@Entity` en TypeORM):**
   - Definiciones puras de tablas en `apps/server/src/server/models/schema.py`.

---

## 🧵 5. Procesos, Hilos y Tareas Programadas (Node.js vs Python)

Una de las mayores diferencias que notarás al pasar de Node.js a Python es el modelo de ejecución de concurrencia y cómo afecta a los temporizadores (schedulers/cron jobs).

### 🟢 Node.js (El modelo Event Loop)
- Node.js es **mono-hilo** por diseño para tu código de JS, manejando la concurrencia a través del Event Loop y operaciones I/O no bloqueantes.
- En producción (ej. con PM2 cluster mode), levantas N instancias separadas del proceso. Si configuras un `setInterval` o un planificador en tu código, **cada proceso independiente ejecutará su propio scheduler**.

### 🐍 Python/Flask (El modelo multi-proceso WSGI)
- Flask es un framework síncrono que no cuenta con un Event Loop integrado.
- Para servir múltiples peticiones en producción, el servidor WSGI (Gunicorn) levanta **múltiples procesos independientes (workers)**.
- **El problema de APScheduler en Flask:** Si inicializas un `BackgroundScheduler` dentro del factory `create_app()`, cada worker que levante Gunicorn ejecutará su propio scheduler. Si tienes 4 workers, tu tarea programada se ejecutará **4 veces**, duplicando ejecuciones y notificaciones.
- **La solución (Desacoplamiento):** Al igual que crearías un `worker.js` independiente en Node, en Python separamos el programador en su propio script ejecutable: `scheduler.py` (corriendo en un proceso único y dedicado bajo un `BlockingScheduler` que bloquea el hilo principal del script).

---

## 💡 Consejos de Sintaxis y Tips para Desarrolladores de JS

1. **`async/await`**: Funciona de forma muy similar.
   - En JS: `async function foo() { await bar(); }`
   - En Python: `async def foo(): await bar()`
   - *Diferencia clave:* En Python, no puedes usar `await` fuera de una función `async` (no hay top-level await directo sin usar `asyncio.run()`).
2. **Diccionarios (`dict`) vs Objetos Literales**:
   - En JS creas un objeto con `{ name: "Luis", age: 30 }` y accedes con `obj.name`.
   - En Python, los diccionarios se escriben como `{"name": "Luis", "age": 30}` y **debes** acceder por clave usando corchetes `obj["name"]` (o `obj.get("name")` para evitar excepciones si la clave no existe).
3. **Tipado Dinámico vs Estático**:
   - En JS utilizas TypeScript para el tipado estático que desaparece al compilar.
   - En Python, usas **Type Hints** (ej: `def greet(name: str) -> str:`). Son informativos y excelentes para el autocompletado en tu IDE, pero **Python no los valida de forma estricta en tiempo de ejecución por sí solo**, a menos que uses librerías como **Pydantic** para forzar la validación de datos externos.
4. **Snake Case (`snake_case`)**:
   - Mientras en JS la convención estándar es usar `camelCase` para variables y funciones, en Python la convención comunitaria estándar (PEP 8) es usar `snake_case` (ej. `get_user_by_id` en lugar de `getUserById`).

---

Con esta guía tienes todo lo necesario para moverte con total soltura por el codebase de **PriceOwl**. ¡A programar! 🦉🚀
