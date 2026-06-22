"""
Funciones para comparar la apuesta del usuario (guess) con el juego objetivo (target).
Ambos son dicts con las keys: name, released_year, platforms (list), genres (list),
developers (list), metacritic, pegi, esrb
"""

def normalize_str(s):
    if s is None:
        return ""
    return str(s).strip().lower()

def compare_sets(guess_list, target_list):
    gset = set([normalize_str(x) for x in (guess_list or []) if x])
    tset = set([normalize_str(x) for x in (target_list or []) if x])
    exact = gset == tset and len(gset) > 0
    intersection = sorted(list(gset & tset))
    return {"exact": exact, "matches": intersection, "guess": sorted(list(gset)), "target": sorted(list(tset))}

def compare_games(guess, target):
    result = {}
    result["name"] = normalize_str(guess.get("name")) == normalize_str(target.get("name"))

    result["released_year"] = guess.get("released_year") == target.get("released_year")
    result["metacritic"] = guess.get("metacritic") == target.get("metacritic")
    result["esrb"] = normalize_str(guess.get("esrb")) == normalize_str(target.get("esrb"))
    result["pegi"] = normalize_str(guess.get("pegi")) == normalize_str(target.get("pegi"))

    result["platforms"] = compare_sets(guess.get("platforms"), target.get("platforms"))
    result["genres"] = compare_sets(guess.get("genres"), target.get("genres"))
    result["developers"] = compare_sets(guess.get("developers"), target.get("developers"))

    return result
