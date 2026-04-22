import argparse
import json
import os
import time
import warnings
from datetime import datetime, timezone
from typing import Optional, Union

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL*")

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY") or os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CACHE_PATH = os.path.join(os.path.dirname(__file__), ".weather_cache.json")
CACHE_TTL_SECONDS = 10 * 60


def _wind_direction(deg: Optional[Union[float, int]]) -> str:
    if deg is None:
        return "—"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((float(deg) + 22.5) // 45) % 8
    return dirs[idx]


def _format_local_time(utc_seconds: int, tz_offset_seconds: int) -> str:
    dt = datetime.fromtimestamp(utc_seconds, tz=timezone.utc).timestamp() + tz_offset_seconds
    return datetime.fromtimestamp(dt).strftime("%H:%M")


def _load_cache() -> dict:
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_cache(cache: dict) -> None:
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _cache_key(city: str, units: str, lang: str) -> str:
    return f"{city.strip().lower()}|{units}|{lang}"


def fetch_weather(city: str, *, units: str = "metric", lang: str = "el", use_cache: bool = True) -> dict:
    if not API_KEY:
        raise RuntimeError("Λείπει API key. Βάλε `API_KEY=...` στο `.env`.")

    key = _cache_key(city, units, lang)
    now = int(time.time())

    if use_cache:
        cache = _load_cache()
        hit = cache.get(key)
        if hit and (now - int(hit.get("ts", 0))) <= CACHE_TTL_SECONDS:
            return hit["data"]

    params = {"q": city, "appid": API_KEY, "units": units, "lang": lang}
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        raise RuntimeError(f"Πρόβλημα δικτύου: {e}") from e

    try:
        data = resp.json()
    except ValueError as e:
        raise RuntimeError("Μη έγκυρη απάντηση από το API.") from e

    if resp.status_code != 200:
        msg = data.get("message", "Άγνωστο σφάλμα")
        raise RuntimeError(f"API error: {msg}")

    if use_cache:
        cache = _load_cache()
        cache[key] = {"ts": now, "data": data}
        _save_cache(cache)

    return data


def print_weather(data: dict, *, units: str = "metric") -> None:
    temp_unit = "°C" if units == "metric" else "°F"
    wind_unit = "m/s" if units == "metric" else "mph"

    city = data.get("name", "—")
    country = data.get("sys", {}).get("country", "—")
    desc = (data.get("weather") or [{}])[0].get("description", "—")

    main = data.get("main", {})
    wind = data.get("wind", {})
    sys = data.get("sys", {})
    tz_offset = int(data.get("timezone", 0))

    sunrise = sys.get("sunrise")
    sunset = sys.get("sunset")
    sunrise_s = _format_local_time(int(sunrise), tz_offset) if sunrise else "—"
    sunset_s = _format_local_time(int(sunset), tz_offset) if sunset else "—"
    deg = wind.get("deg")
    deg_part = f" {deg}°" if deg is not None else ""

    print(f"\n📍 {city}, {country}")
    print(f"🌤️  Καιρός: {desc}")
    print(f"🌡️  Θερμοκρασία: {main.get('temp', '—')}{temp_unit} (αίσθηση {main.get('feels_like', '—')}{temp_unit})")
    print(f"⬇️  Ελάχιστη/Μέγιστη: {main.get('temp_min', '—')}{temp_unit} / {main.get('temp_max', '—')}{temp_unit}")
    print(f"💧 Υγρασία: {main.get('humidity', '—')}% | 🧭 Πίεση: {main.get('pressure', '—')} hPa")
    print(
        f"💨 Άνεμος: {wind.get('speed', '—')} {wind_unit}"
        f" ({_wind_direction(deg)}{deg_part})"
    )
    print(f"🌅 Ανατολή: {sunrise_s} | 🌇 Δύση: {sunset_s}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Weather app (OpenWeatherMap)")
    p.add_argument("--city", "-c", help="Πόλη (αν δοθεί, τρέχει non-interactive)")
    p.add_argument("--units", choices=["metric", "imperial"], default="metric", help="Μονάδες (default: metric)")
    p.add_argument("--lang", default="el", help="Γλώσσα περιγραφής καιρού (default: el)")
    p.add_argument("--no-cache", action="store_true", help="Απενεργοποίηση cache")
    return p


def interactive_loop(units: str, lang: str, use_cache: bool) -> None:
    while True:
        city = input("\nΔώσε πόλη (ή 'q' για έξοδο): ").strip()
        if not city:
            continue
        if city.lower() == "q":
            print("Αντίο! 👋")
            break
        try:
            data = fetch_weather(city, units=units, lang=lang, use_cache=use_cache)
            print_weather(data, units=units)
        except RuntimeError as e:
            print(f"❌ {e}")


def main() -> int:
    args = build_parser().parse_args()
    use_cache = not args.no_cache

    if args.city:
        try:
            data = fetch_weather(args.city, units=args.units, lang=args.lang, use_cache=use_cache)
            print_weather(data, units=args.units)
            return 0
        except RuntimeError as e:
            print(f"❌ {e}")
            return 1

    interactive_loop(args.units, args.lang, use_cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())