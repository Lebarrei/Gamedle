#!/usr/bin/env python3
"""
Importador desde RAWG -> Supabase.
Usar SUPABASE_SERVICE_KEY en .env para escribir en la tabla 'games'.
"""

import requests
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

RAWG_KEY = os.getenv("RAWG_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not (RAWG_KEY and SUPABASE_URL and SUPABASE_SERVICE_KEY):
    raise SystemExit("Define RAWG_KEY, SUPABASE_URL y SUPABASE_SERVICE_KEY en el .env")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def fetch_game_details(rawg_id):
    url = f"https://api.rawg.io/api/games/{rawg_id}"
    r = requests.get(url, params={"key": RAWG_KEY})
    r.raise_for_status()
    return r.json()

def normalize_game(raw):
    released = raw.get("released")
    year = None
    if released:
        try:
            year = int(released.split("-")[0])
        except Exception:
            year = None
    def safe_list_of_names(items, nested_key=None):
        if not items:
            return []
        out = []
        for it in items:
            if nested_key:
                val = it.get(nested_key, {}).get("name")
            else:
                val = it.get("name")
            if val:
                out.append(val)
        return out

    platforms = []
    for p in raw.get("platforms", []):
        plat = p.get("platform", {}).get("name")
        if plat:
            platforms.append(plat)

    return {
        "id": raw["id"],
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "released_date": released,
        "released_year": year,
        "platforms": platforms,
        "genres": safe_list_of_names(raw.get("genres", [])),
        "developers": safe_list_of_names(raw.get("developers", [])),
        "modes": safe_list_of_names(raw.get("tags", [])),  # tags como proxy de modos si aplica
        "metacritic": raw.get("metacritic"),
        "pegi": None,
        "esrb": raw.get("esrb_rating", {}).get("name") if raw.get("esrb_rating") else None,
        "rawg_url": raw.get("website") or raw.get("slug")
    }

def upsert_game(record):
    # Supabase upsert
    res = supabase.table("games").upsert(record).execute()
    return res

def import_pages(pages=10, page_size=40, delay_between_requests=0.25):
    base = "https://api.rawg.io/api/games"
    for page in range(1, pages + 1):
        print(f"Fetching page {page}")
        r = requests.get(base, params={"key": RAWG_KEY, "page": page, "page_size": page_size})
        r.raise_for_status()
        data = r.json()
        for g in data.get("results", []):
            try:
                detail = fetch_game_details(g["id"])
                record = normalize_game(detail)
                upsert_game(record)
                print(f"Upserted {record['id']} - {record['name']}")
            except Exception as e:
                print(f"Error importing {g.get('id')}: {e}")
            time.sleep(delay_between_requests)
        # pequeño descanso entre páginas
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=20, help="Número de páginas a importar")
    parser.add_argument("--page-size", type=int, default=40, help="Tamaño de página RAWG")
    args = parser.parse_args()
    import_pages(pages=args.pages, page_size=args.page_size)
