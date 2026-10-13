# Liga Barrial La Armenia — Backend

API REST para la administración de la Liga Barrial La Armenia: equipos,
jugadores, partidos, vocalías, sanciones, finanzas, seguros, documentos,
noticias y estadísticas.

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
- `uv` instalado ([guía](https://docs.astral.sh/uv/))
- Node.js ≥ 20.19 (solo si vas a correr el frontend)

---

## Setup

### 1. Clonar e instalar dependencias

```bash
git clone <repo-url> ldbla
cd ldbla
uv sync