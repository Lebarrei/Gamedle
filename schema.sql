-- Esquema para Supabase/Postgres: tabla games + tabla daily_picks
CREATE TABLE IF NOT EXISTS games (
  id bigint PRIMARY KEY,     -- id de RAWG
  name text NOT NULL,
  slug text,
  released_date date,
  released_year int,
  platforms text[],          -- array de nombres
  genres text[],             -- array de nombres
  developers text[],         -- array de nombres
  modes text[],              -- modos o tags relevantes
  metacritic int,
  pegi text,
  esrb text,
  rawg_url text,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_games_name ON games (lower(name));
CREATE INDEX IF NOT EXISTS idx_games_released_year ON games (released_year);

-- Tabla opcional para picks diarios
CREATE TABLE IF NOT EXISTS daily_picks (
  pick_date date PRIMARY KEY,
  game_id bigint REFERENCES games(id),
  created_at timestamptz DEFAULT now()
);
