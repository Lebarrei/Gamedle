#!/usr/bin/env python3
"""
App Streamlit minimal para jugar:
- Elige juego del día de forma determinística por fecha.
- Permite buscar por nombre y comparar con el objetivo.
"""

import os
import hashlib
import datetime
from dotenv import load_dotenv
from supabase import create_client
import streamlit as st
from compare import compare_games

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not (SUPABASE_URL and SUPABASE_ANON_KEY):
    st.error("Define SUPABASE_URL y SUPABASE_ANON_KEY en el .env")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@st.cache_data
def get_all_ids():
    res = supabase.table("games").select("id").execute()
    data = getattr(res, "data", None) or res.get("data") or []
    return [r["id"] for r in data]

@st.cache_data
def get_game_by_id(game_id):
    res = supabase.table("games").select("*").eq("id", game_id).single().execute()
    data = getattr(res, "data", None) or res.get("data")
    return data

def choose_daily_game():
    ids = get_all_ids()
    if not ids:
        return None
    today = datetime.date.today().isoformat()
    h = int(hashlib.sha256(today.encode()).hexdigest(), 16)
    idx = h % len(ids)
    return get_game_by_id(ids[idx])

def search_game_by_name(name):
    # ilike search, devuelve hasta 10 candidatos
    res = supabase.table("games").select("*").ilike("name", f"%{name}%").limit(10).execute()
    data = getattr(res, "data", None) or res.get("data") or []
    return data

st.set_page_config(page_title="Gamedle", layout="centered")
st.title("Gamedle — Adivina el videojuego del día")

target = choose_daily_game()
if not target:
    st.warning("No hay juegos en la base de datos. Ejecuta el importador primero.")
    st.stop()

st.sidebar.markdown("Reglas: escribe el nombre de un juego y presiona Enter. Verás feedback por categoría.")

guess_input = st.text_input("Adivina el juego (nombre)")
if guess_input:
    candidates = search_game_by_name(guess_input)
    if not candidates:
        st.info("No encontré coincidencias. Intenta otra búsqueda o corrige la escritura.")
    else:
        # Mostrar lista de candidatos para que el usuario elija
        names = [c["name"] for c in candidates]
        choice = st.selectbox("Selecciona el juego que querías decir:", names)
        guess = next((c for c in candidates if c["name"] == choice), candidates[0])
        feedback = compare_games(guess, target)

        if feedback["name"]:
            st.success(f"¡Has acertado! El juego del día es: {target['name']}")
            st.json(target)
        else:
            st.markdown("### Resultado por categoría")
            def show_line(label, ok, extra=None):
                emoji = "✅" if ok else "❌"
                if extra:
                    st.write(f"{emoji} {label}: {extra}")
                else:
                    st.write(f"{emoji} {label}")
            show_line("Nombre", feedback["name"], f"Tu apuesta: {guess['name']}")
            show_line("Año de salida", feedback["released_year"], f"Tu: {guess.get('released_year')}")
            show_line("Metacritic", feedback["metacritic"], f"Tu: {guess.get('metacritic')}")
            show_line("ESRB", feedback["esrb"], f"Tu: {guess.get('esrb')}")
            show_line("PEGI", feedback["pegi"], f"Tu: {guess.get('pegi')}")
            # Sets
            def show_set(name, info):
                if info["exact"]:
                    st.write(f"✅ {name}: Coinciden exactamente")
                else:
                    st.write(f"❌ {name}: coincidencias parciales: {info['matches']}")
            show_set("Plataformas", feedback["platforms"])
            show_set("Géneros", feedback["genres"])
            show_set("Desarrolladores", feedback["developers"])

            st.info("Sigue intentando. Cuando aciertes el nombre exacto, se revelarán todos los detalles.")
