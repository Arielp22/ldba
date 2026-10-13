# Liga Barrial La Armenia — Backend

API REST para la administración de la Liga Barrial La Armenia: equipos, jugadores, partidos, vocalías, sanciones, finanzas, seguros, documentos, noticias y estadísticas.

---

## Stack

- **Django 5.x** + **Django REST Framework**
- **PostgreSQL**
- **JWT** (`djangorestframework-simplejwt`) con blacklist
- **CORS** (`django-cors-headers`)
- **Filtros** (`django-filter`)
- **Python 3.12** + **uv** como gestor de dependencias

---

## Requisitos

- Python 3.12 o superior
- PostgreSQL 14 o superior
- `uv` instalado ([guía oficial](https://docs.astral.sh/uv/))

---

## Setup

### 1. Clonar e instalar dependencias

```bash
git clone <repo-url> ldbla
cd ldbla
uv sync
```

### 2. Configurar el entorno

Crea un archivo `.env` en la raíz:

```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgres://usuario:password@localhost:5432/ldbla
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Crear la base de datos

```bash
createdb ldbla
```

O desde PostgreSQL:

```sql
CREATE DATABASE ldbla;
CREATE USER ldbla_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE ldbla TO ldbla_user;
```

### 4. Aplicar migraciones

```bash
uv run python manage.py migrate
```

### 5. Crear grupos y permisos

```bash
uv run python manage.py create_groups
```

Este comando crea los 8 grupos del sistema:

| Grupo | Permisos |
|---|---|
| `Superadmin` | Todos |
| `Comision Administrativa` | Sesiones, documentos, noticias |
| `Comision Financiera` | Movimientos financieros, informes |
| `Comision Tecnica` | Temporadas, categorías, jornadas, partidos, vocalías |
| `Comision Calificaciones` | Jugadores, plantillas, capitanes |
| `Comision Penas` | Sanciones, multas, recibos |
| `Comision Seguro` | Lesiones |
| `Administrador Equipo` | Solo lectura de su equipo |

Para reasignar permisos:

```bash
uv run python manage.py create_groups --reset
```

### 6. Crear superusuario

```bash
uv run python manage.py createsuperuser
```

### 7. Arrancar el servidor

```bash
uv run python manage.py runserver
```

- API: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/

---

## Estructura del proyecto

```
ldbla/
├── armenia/                        # app principal
│   ├── management/commands/
│   │   └── create_groups.py
│   ├── migrations/
│   ├── models/                     # entidades por dominio
│   ├── serializers/                # validación + transformación
│   ├── views/                      # ViewSets y APIViews
│   ├── services/
│   │   └── estadisticas.py         # tabla de posiciones, goleadores
│   ├── admin.py
│   ├── pagination.py               # StandardPagination
│   ├── permissions.py              # permisos por comisión
│   └── urls.py
├── config/                         # settings + urls del proyecto
├── .env
├── manage.py
├── pyproject.toml
└── uv.lock
```

---

## Modelo de datos

### 22 tablas propias

| Bloque | Tablas |
|---|---|
| Configuración base | `temporada`, `categoria` |
| Equipos | `equipo`, `equipo_temporada_categoria` |
| Jugadores | `jugador`, `jugador_equipo_temporada`, `capitan_equipo_temporada` |
| Competencia | `jornada`, `partido` |
| Vocalías | `vocalia`, `vocalia_jugador` |
| Sanciones | `sancion`, `historial_sancion`, `multa`, `recibo` |
| Finanzas | `movimiento_financiero`, `informe_financiero_semanal` |
| Seguro | `lesion` |
| Administración | `sesion`, `sesion_participante`, `documento`, `noticia` |

Más las tablas estándar de Django (`auth_user`, `auth_group`, `auth_permission`, `token_blacklist_*`).

### Detalle de tablas

#### Configuración base

**`core_temporada`**

| Campo | Tipo | Notas |
|---|---|---|
| `id` | AutoField | PK |
| `nombre` | CharField(100) | Único |
| `anio` | PositiveInteger | |
| `fecha_inicio`, `fecha_fin` | DateField | |
| `estado` | ChoiceField | `planificada` / `en_curso` / `finalizada` / `cancelada` |
| `created_at`, `updated_at` | DateTimeField | |

**`core_categoria`**

| Campo | Tipo | Notas |
|---|---|---|
| `id` | AutoField | PK |
| `nombre` | CharField(100) | Único |
| `descripcion` | TextField | Nullable |
| `activa` | BooleanField | Default `True` |
| `created_at`, `updated_at` | DateTimeField | |

#### Equipos

**`core_equipo`**

| Campo | Tipo | Notas |
|---|---|---|
| `id` | AutoField | PK |
| `nombre` | CharField(150) | Único |
| `siglas` | CharField(10) | Nullable |
| `color_principal`, `color_secundario` | CharField(30) | Nullable |
| `logo` | CharField(255) | Solo ruta |
| `presidente` | CharField(150) | Nullable |
| `telefono` | CharField(30) | Nullable |
| `email` | EmailField | Nullable |
| `activo` | BooleanField | Default `True` |
| `user` | OneToOneField → User | **Obligatorio**, `on_delete=PROTECT` |
| `created_at`, `updated_at` | DateTimeField | |

**Regla:** 1 equipo = 1 usuario. Cambio de presidente = `reset-password`.

**`core_equipo_temporada_categoria`**

| Campo | Tipo |
|---|---|
| `equipo` | FK → Equipo |
| `temporada` | FK → Temporada |
| `categoria` | FK → Categoria |
| `activo` | BooleanField |

**Restricción:** `unique_together = (equipo, temporada, categoria)`.

#### Jugadores

**`core_jugador`**

| Campo | Tipo | Notas |
|---|---|---|
| `nombres`, `apellidos` | CharField(150) | |
| `cedula` | CharField(20) | Único |
| `fecha_nacimiento` | DateField | |
| `telefono` | CharField(30) | Nullable |
| `email` | EmailField | Nullable |
| `direccion` | CharField(255) | Nullable |
| `foto` | CharField(255) | Solo ruta |
| `numero_carnet` | CharField(30) | Único, nullable |
| `estado_calificacion` | ChoiceField | `pendiente` / `calificado` / `rechazado` / `inhabilitado` |
| `observaciones` | TextField | |
| `activo` | BooleanField | Default `True` |

**`core_jugador_equipo_temporada`**

| Campo | Tipo |
|---|---|
| `jugador` | FK → Jugador |
| `equipo` | FK → Equipo |
| `temporada` | FK → Temporada |
| `categoria` | FK → Categoria |
| `activo` | BooleanField |

**Restricción:** `unique_together = (jugador, temporada, categoria)`.

**Regla:** un jugador solo puede estar en 1 equipo por temporada + categoría. Puede estar en varias categorías.

**`core_capitan_equipo_temporada`**

| Campo | Tipo |
|---|---|
| `equipo` | FK → Equipo |
| `jugador` | FK → Jugador |
| `temporada` | FK → Temporada |
| `categoria` | FK → Categoria |
| `activo` | BooleanField |

**Restricción:** `unique_together = (equipo, temporada, categoria)`.

#### Competencia

**`core_jornada`**

| Campo | Tipo |
|---|---|
| `temporada` | FK → Temporada |
| `categoria` | FK → Categoria |
| `numero` | PositiveInteger |
| `fecha_sabado`, `fecha_domingo` | DateField |
| `estado` | ChoiceField |

**Restricción:** `unique_together = (temporada, categoria, numero)`.

**`core_partido`**

| Campo | Tipo | Notas |
|---|---|---|
| `jornada` | FK → Jornada | |
| `numero_partido` | PositiveInteger | 1 a 5 |
| `dia` | ChoiceField | `sabado` / `domingo` |
| `hora` | TimeField | 08:00, 10:00, 12:00, 14:00, 16:00 |
| `equipo_local`, `equipo_visitante` | FK → Equipo | `on_delete=PROTECT` |
| `equipo_vocal` | FK → Equipo | Nullable, asignado por sorteo |
| `goles_local`, `goles_visitante` | PositiveInteger | Nullable |
| `estado` | ChoiceField | `programado` / `en_curso` / `finalizado` / `suspendido` / `cancelado` |
| `observaciones` | TextField | |

**Restricción:** `unique_together = (jornada, dia, numero_partido)`.

**Validaciones (serializer):**
- `equipo_local != equipo_visitante`
- `equipo_vocal != equipo_local` y `!= equipo_visitante`
- Un equipo no puede ser vocal 2 veces el mismo día en la misma jornada

#### Vocalías

**`core_vocalia`**

| Campo | Tipo |
|---|---|
| `partido` | OneToOneField → Partido, nullable |
| `arbitro` | CharField(150) |
| `vocal` | CharField(150) |
| `goles_local`, `goles_visitante` | PositiveInteger, nullable |
| `informe` | TextField |
| `firma_arbitro`, `firma_vocal` | CharField(255) |
| `estado` | ChoiceField: `borrador` / `enviada` / `aprobada` / `rechazada` |
| `observaciones_rechazo` | TextField |

**`core_vocalia_jugador`**

| Campo | Tipo |
|---|---|
| `vocalia` | FK → Vocalia |
| `jugador` | FK → Jugador |
| `equipo` | FK → Equipo |
| `goles` | PositiveInteger (default 0) |
| `tarjeta_amarilla`, `tarjeta_roja` | BooleanField |
| `es_capitan` | BooleanField |
| `ingreso_minuto`, `salida_minuto` | PositiveInteger, nullable |

**Restricción:** `unique_together = (vocalia, jugador)`.

#### Sanciones y multas

**`core_sancion`**

| Campo | Tipo |
|---|---|
| `tipo` | ChoiceField: `jugador` / `equipo` |
| `jugador`, `equipo` | FK, nullable |
| `partido`, `vocalia` | FK, nullable |
| `motivo` | CharField(255) |
| `articulo` | CharField(100) |
| `fecha_inicio`, `fecha_fin` | DateField |
| `dias`, `partidos_sancion` | PositiveInteger |
| `estado` | ChoiceField: `activa` / `cumplida` / `apelada` / `anulada` |
| `observaciones` | TextField |

**`core_historial_sancion`** (auditoría automática)

| Campo | Tipo |
|---|---|
| `sancion` | FK → Sancion |
| `estado_anterior`, `estado_nuevo` | CharField(20) |
| `motivo_cambio` | TextField |
| `usuario` | FK → User |

**`core_multa`**

| Campo | Tipo |
|---|---|
| `sancion` | FK → Sancion, nullable |
| `equipo` | FK → Equipo, nullable |
| `monto` | Decimal(10,2) |
| `motivo` | CharField(255) |
| `estado` | ChoiceField: `pendiente` / `pagada` / `condonada` |
| `fecha_pago` | DateField, nullable |
| `forma_pago` | ChoiceField: `efectivo` / `transferencia` / `deposito` / `otro` |

**Validación:** si `estado=pagada`, requiere `fecha_pago` + `forma_pago`.

**`core_recibo`**

| Campo | Tipo |
|---|---|
| `multa` | OneToOneField → Multa |
| `numero` | CharField(50), único |
| `entregado_a`, `entregado_por` | CharField(150) |
| `fecha_entrega` | DateField |

#### Finanzas

**`core_movimiento_financiero`**

| Campo | Tipo |
|---|---|
| `tipo` | ChoiceField: `ingreso` / `egreso` |
| `concepto` | CharField(255) |
| `fecha` | DateField |
| `valor` | Decimal(12,2) |
| `responsable` | CharField(150) |
| `comprobante` | CharField(255) |

**Validación:** `valor > 0`.

**`core_informe_financiero_semanal`**

| Campo | Tipo |
|---|---|
| `numero_semana` | PositiveInteger (1-53) |
| `anio` | PositiveInteger |
| `fecha_semana` | DateField |
| `cerveza`, `boleteria`, `multas`, `otros_ingresos`, `egresos` | Decimal(12,2) |
| `estado` | ChoiceField: `borrador` / `presentado` / `aprobado` |

**Restricción:** `unique_together = (numero_semana, anio)`.

**Propiedades calculadas:** `total_ingresos`, `balance`.

#### Seguro

**`core_lesion`**

| Campo | Tipo |
|---|---|
| `jugador` | FK → Jugador |
| `equipo`, `partido`, `vocalia` | FK, nullable |
| `fecha` | DateField |
| `tipo` | ChoiceField: `esguince` / `fractura` / `desgarro` / `contusion` / `luxacion` / `otro` |
| `gravedad` | ChoiceField: `leve` / `moderada` / `grave` |
| `descripcion` | TextField |
| `monto_apoyo` | Decimal(10,2), nullable |
| `estado` | ChoiceField: `reportada` / `en_revision` / `aprobada` / `rechazada` / `pagada` |

#### Administración

**`core_sesion`**

| Campo | Tipo |
|---|---|
| `fecha` | DateField |
| `tipo` | ChoiceField: `ordinaria` / `extraordinaria` |
| `orden_del_dia`, `acta` | TextField |
| `estado` | ChoiceField: `programada` / `en_curso` / `finalizada` / `cancelada` |

**`core_sesion_participante`**

| Campo | Tipo |
|---|---|
| `sesion` | FK → Sesion |
| `nombre`, `cargo` | CharField(150) |
| `presente` | BooleanField |
| `observaciones` | CharField(255) |

**`core_documento`**

| Campo | Tipo |
|---|---|
| `tipo` | ChoiceField: `cedula` / `acta` / `factura` / `informe` / `carnet` / `otro` |
| `titulo` | CharField(255) |
| `descripcion` | TextField |
| `archivo` | CharField(500) — ruta/URL |
| `mime_type` | CharField(100) |
| `tamano_bytes` | PositiveInteger |
| `jugador`, `equipo`, `sesion` | FK, nullable |

**`core_noticia`**

| Campo | Tipo |
|---|---|
| `titulo` | CharField(255) |
| `resumen` | CharField(500) |
| `contenido` | TextField |
| `imagen` | CharField(500) |
| `autor` | CharField(150) |
| `publicada`, `destacada` | BooleanField |
| `fecha_publicacion` | DateTimeField, nullable |

---

## API REST

Todas las rutas están bajo `/api/`.

### Autenticación

| Método | Endpoint | Auth |
|---|---|---|
| POST | `/api/auth/register/` | No |
| POST | `/api/auth/login/` | No |
| POST | `/api/auth/token/refresh/` | No |
| POST | `/api/auth/token/verify/` | No |
| POST | `/api/auth/logout/` | Sí (JWT) |
| GET | `/api/auth/me/` | Sí (JWT) |

**Login body:**

```json
{ "username": "admin", "password": "tu-password" }
```

**Login response:**

```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user_id": 1,
  "username": "admin",
  "email": "admin@liga.com",
  "is_staff": true,
  "is_superuser": true,
  "groups": ["Superadmin"]
}
```

Todas las rutas autenticadas requieren `Authorization: Bearer <access>`.

### Usuarios (admin)

| Método | Endpoint |
|---|---|
| GET/POST | `/api/users/` |
| GET/PUT/PATCH/DELETE | `/api/users/{id}/` |
| GET/PATCH | `/api/users/profile/` |
| POST | `/api/users/change-password/` |
| POST | `/api/users/{id}/toggle-active/` |
| GET | `/api/users/stats/` |

Filtros: `is_staff`, `is_active`. Búsqueda: `username`, `email`, `first_name`, `last_name`.

### Temporadas y Categorías

| Método | Endpoint |
|---|---|
| GET/POST | `/api/temporadas/` |
| GET/PUT/PATCH/DELETE | `/api/temporadas/{id}/` |
| GET/POST | `/api/categorias/` |
| GET/PUT/PATCH/DELETE | `/api/categorias/{id}/` |

Filtros temporadas: `estado`, `anio`. Filtros categorías: `activa`.

### Equipos

| Método | Endpoint |
|---|---|
| GET/POST | `/api/equipos/` |
| GET/PUT/PATCH/DELETE | `/api/equipos/{id}/` |
| POST | `/api/equipos/{id}/reset-password/` (Superadmin) |
| GET/POST | `/api/equipos-temporada-categoria/` |
| GET/PUT/PATCH/DELETE | `/api/equipos-temporada-categoria/{id}/` |

**Crear equipo body:**

```json
{
  "nombre": "Atlético Armenia",
  "siglas": "AAR",
  "presidente": "Juan Pérez",
  "username": "atletico_armenia",
  "password": "Equipo2025!"
}
```

### Jugadores

| Método | Endpoint |
|---|---|
| GET/POST | `/api/jugadores/` |
| GET/PUT/PATCH/DELETE | `/api/jugadores/{id}/` |
| POST | `/api/jugadores/{id}/calificar/` |
| GET/POST | `/api/jugadores-equipo-temporada/` |
| GET/PUT/PATCH/DELETE | `/api/jugadores-equipo-temporada/{id}/` |
| GET/POST | `/api/capitanes-equipo-temporada/` |
| GET/PUT/PATCH/DELETE | `/api/capitanes-equipo-temporada/{id}/` |

### Jornadas y Partidos

| Método | Endpoint |
|---|---|
| GET/POST | `/api/jornadas/` |
| GET/PUT/PATCH/DELETE | `/api/jornadas/{id}/` |
| GET | `/api/jornadas/{id}/resumen/` |
| POST | `/api/jornadas/{id}/sortear-vocalias/` |
| GET/POST | `/api/partidos/` |
| GET/PUT/PATCH/DELETE | `/api/partidos/{id}/` |
| POST | `/api/partidos/{id}/resultado/` |

### Vocalías

| Método | Endpoint |
|---|---|
| GET/POST | `/api/vocalias/` |
| GET/PUT/PATCH/DELETE | `/api/vocalias/{id}/` |
| POST | `/api/vocalias/{id}/aprobar/` |
| POST | `/api/vocalias/{id}/rechazar/` |
| POST | `/api/vocalias/{id}/sincronizar-resultado/` |
| GET/POST | `/api/vocalia-jugadores/` |
| GET/PUT/PATCH/DELETE | `/api/vocalia-jugadores/{id}/` |

### Sanciones, Multas y Recibos

| Método | Endpoint |
|---|---|
| GET/POST | `/api/sanciones/` |
| GET/PUT/PATCH/DELETE | `/api/sanciones/{id}/` |
| POST | `/api/sanciones/{id}/cambiar-estado/` |
| GET | `/api/historial-sanciones/` |
| GET/POST | `/api/multas/` |
| GET/PUT/PATCH/DELETE | `/api/multas/{id}/` |
| POST | `/api/multas/{id}/marcar-pagada/` |
| GET/POST | `/api/recibos/` |
| GET/PUT/PATCH/DELETE | `/api/recibos/{id}/` |

### Finanzas

| Método | Endpoint |
|---|---|
| GET/POST | `/api/movimientos-financieros/` |
| GET/PUT/PATCH/DELETE | `/api/movimientos-financieros/{id}/` |
| GET | `/api/movimientos-financieros/resumen/` |
| GET/POST | `/api/informes-financieros-semanales/` |
| GET/PUT/PATCH/DELETE | `/api/informes-financieros-semanales/{id}/` |

### Seguro

| Método | Endpoint |
|---|---|
| GET/POST | `/api/lesiones/` |
| GET/PUT/PATCH/DELETE | `/api/lesiones/{id}/` |
| POST | `/api/lesiones/{id}/cambiar-estado/` |

### Administración

| Método | Endpoint |
|---|---|
| GET/POST | `/api/sesiones/` |
| GET/PUT/PATCH/DELETE | `/api/sesiones/{id}/` |
| POST | `/api/sesiones/{id}/finalizar/` |
| GET/POST | `/api/sesion-participantes/` |
| GET/PUT/PATCH/DELETE | `/api/sesion-participantes/{id}/` |
| GET/POST | `/api/documentos/` |
| GET/PUT/PATCH/DELETE | `/api/documentos/{id}/` |
| GET/POST | `/api/noticias/` |
| GET/PUT/PATCH/DELETE | `/api/noticias/{id}/` |
| POST | `/api/noticias/{id}/publicar/` |
| POST | `/api/noticias/{id}/despublicar/` |

### Endpoints públicos (sin login)

| Método | Endpoint |
|---|---|
| GET | `/api/publico/temporadas/` |
| GET | `/api/publico/categorias/` |
| GET | `/api/publico/equipos/` |
| GET | `/api/publico/jornadas/` |
| GET | `/api/publico/partidos/` |
| GET | `/api/publico/partidos/proximos/` |
| GET | `/api/publico/partidos/recientes/` |
| GET | `/api/publico/tabla-posiciones/` |
| GET | `/api/publico/goleadores/` |
| GET | `/api/publico/tarjetas/` |
| GET | `/api/publico/noticias/` |

Query params para estadísticas: `temporada` (obligatorio), `categoria` (opcional), `limit` (opcional).

---

## Reglas de negocio

1. **1 equipo = 1 usuario** (OneToOne). Cambio de presidente = `reset-password`.
2. **No se eliminan equipos.** Se inactivan. El `DELETE` devuelve 405.
3. **1 jugador por temporada + categoría.** Puede jugar en varias categorías.
4. **Vocalía:** el equipo vocal no puede ser local ni visitante; no puede vocalizar 2 veces el mismo día.
5. **Emparejamiento de vocalías:** `P1→P3, P2→P1, P3→P2, P4↔P5` por día, aplicado a sábado y domingo por separado.
6. **5 partidos por día**, sábado y domingo → 10 partidos por jornada.
7. **Horarios permitidos:** 08:00, 10:00, 12:00, 14:00, 16:00.
8. **Árbitros y vocales:** texto libre, sin catálogo.
9. **Tabla de posiciones y goleadores:** se calculan, no se almacenan.
10. **No se guardan archivos** en la BD (solo rutas/metadatos).
11. **No hay registro público de usuarios.**
12. **Informe semanal:** único por `(numero_semana, anio)`.
13. **Multa pagada:** requiere `fecha_pago` + `forma_pago`.
14. **Recibo:** único por multa y `numero` único.
15. **Un partido = una vocalía** (OneToOne).
16. **Sanciones:** tipo `jugador` requiere `jugador`; tipo `equipo` requiere `equipo`.

### Cálculos de estadísticas

Implementados en `armenia/services/estadisticas.py`.

**Tabla de posiciones:**
- Solo cuenta partidos con `estado=finalizado` y resultado
- Puntos: victoria = 3, empate = 1, derrota = 0
- Desempate: puntos → diferencia de gol → goles a favor → nombre

**Goleadores:**
- Suma `goles` desde `VocaliaJugador` agrupado por jugador
- Ordena por total descendente

**Tarjetas:**
- Cuenta `tarjeta_amarilla` y `tarjeta_roja` por jugador
- Devuelve jugador, equipo, amarillas, rojas, total

---

## Cómo crear un módulo nuevo

1. Crear modelo en `armenia/models/<nombre>.py`
2. Registrarlo en `armenia/models/__init__.py`
3. Crear serializer en `armenia/serializers/<nombre>.py`
4. Crear viewset en `armenia/views/<nombre>.py`
5. Registrar en `armenia/admin.py`
6. Registrar en `armenia/urls.py`
7. Agregar permisos en `armenia/management/commands/create_groups.py`
8. Correr migraciones y `create_groups`:

```bash
uv run python manage.py makemigrations armenia
uv run python manage.py migrate
uv run python manage.py create_groups
```

---

## Configuración clave

### `settings.py`

```python
INSTALLED_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'armenia',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'armenia.pagination.StandardPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### `config/urls.py`

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('armenia.urls')),
]
```

---

## Despliegue

### Variables de entorno en producción

```env
DEBUG=False
SECRET_KEY=<genera-con-secrets.token_urlsafe>
DATABASE_URL=<url-postgres-produccion>
CORS_ALLOWED_ORIGINS=https://tudominio.com
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
```

### Comandos

```bash
uv run python manage.py collectstatic --no-input
uv run python manage.py migrate
uv run python manage.py create_groups
uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Opciones de hosting

- Railway / Fly.io / Render (con Postgres incluido)
- VPS: Nginx + Gunicorn + PostgreSQL
- DB: Neon, Supabase, RDS

---

## Referencias

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [django-filter](https://django-filter.readthedocs.io/)
- [django-cors-headers](https://github.com/adamchainz/django-cors-headers)

---

## Licencia

Proyecto privado de la Liga Barrial La Armenia.