# API Sonar

Este proyecto es una API REST construida con **FastAPI** y **SQLModel**. Proporciona funcionalidades para la gestión de usuarios, estados, seguimiento de pantallas, y una mecánica de juego de dados con reclamaciones de valores.

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal.
- **FastAPI**: Framework web moderno y rápido para construir APIs.
- **SQLModel**: Librería para interactuar con bases de datos SQL desde Python.
- **Uvicorn**: Servidor ASGI para ejecutar la aplicación (asumido).

## Instalación

1. Clona el repositorio:

```bash
git clone <url-del-repositorio>
cd api-sonar
```

2. Crea un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Para iniciar el servidor de desarrollo, ejecuta:

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`.

Puedes acceder a la documentación interactiva generada automáticamente por Swagger UI en `http://localhost:8000/docs`.

## Modelos de Datos

### User

Representa a un usuario del sistema.

- `id`: Identificador único.
- `state`: Estado del usuario (0, 1 o 2).
- `group_id`: ID del grupo al que pertenece (opcional).
- `thrower`: ID asociado al lanzador (opcional).

### Throw

Registra un lanzamiento de dado.

- `id`: Identificador único.
- `user_id`: ID del usuario que realizó el lanzamiento.
- `value`: Valor del dado (1-6).
- `throw_time`: Marca de tiempo del lanzamiento.

### FirstThrow

Registra la reclamación del primer lanzamiento.

- `id`: Mismo ID que el lanzamiento original.
- `user_id`: ID del usuario.
- `true_value`: Valor real obtenido en el lanzamiento.
- `claimed_value`: Valor reclamado por el usuario.

### Screen

Rastrea los tiempos en que el usuario accede a diferentes pantallas.

- `user_id`: ID del usuario.
- `screen1`, `screen2`, `screen3`: Marcas de tiempo de acceso.

## Endpoints de la API

### Usuarios

- **Crear Usuario**

  - `POST /users/`
  - Body:
    ```json
    {
      "group_id": int | null,
      "thrower": int | null
    }
    ```

- **Obtener Estado de Usuario**

  - `GET /users/{user_id}/state`

- **Actualizar Estado de Usuario**
  - `PATCH /users/{user_id}/state`
  - Body:
    ```json
    {
      "state": int
    }
    ```
  - Nota: El estado debe ser 0, 1 o 2.

### Pantallas

- **Actualizar Pantalla**
  - `POST /users/{user_id}/screens`
  - Body:
    ```json
    {
      "screen_name": "screen1" | "screen2" | "screen3"
    }
    ```

### Juego (Dados)

- **Lanzar Dado**

  - `POST /users/{user_id}/throw`
  - Genera un valor aleatorio entre 1 y 6.

- **Reclamar Primer Lanzamiento**
  - `POST /users/{user_id}/claim-first`
  - Body:
    ```json
    {
      "claimed_value": int
    }
    ```
  - Registra el valor que el usuario dice haber obtenido frente al valor real del primer lanzamiento registrado.

## Migraciones y Base de Datos

El proyecto incluye scripts para manejar la base de datos:

- `database.py`: Configuración de la conexión.
- `migrate.py`: Script para migraciones (revisar su uso específico).
- `seed.py`: Script para poblar la base de datos con datos iniciales.
