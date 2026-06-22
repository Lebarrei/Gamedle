# Gamedle

Juego estilo Wordle enfocado en videojuegos (inspirado en Pokedle).

Estructura:
- schema.sql: esquema de la base de datos para Supabase/Postgres.
- import_rawg.py: script para importar juegos desde la API RAWG a Supabase.
- compare.py: lógica de comparación entre la apuesta y el juego objetivo.
- streamlit_app.py: aplicación Streamlit mínima para jugar.
- requirements.txt: dependencias Python.
- .gitignore: archivos a ignorar.

IMPORTANTE: No incluyas keys directamente en el repositorio. Rellena las variables de entorno tal como se indica en README.md antes de ejecutar.
