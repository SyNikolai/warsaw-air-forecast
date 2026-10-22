"""Build config/stations.yaml: Warsaw GIOŚ stations and their hourly sensors.

For each station, every sensor measuring PM2.5, PM10 or NO2 is probed on the
current-data endpoint. A sensor is kept only if it returns data whose station
code ends in "-1g" (1-hour averaging). Manual sensors answer HTTP 400 with
API-ERR-100003 and are skipped.
"""

from __future__ import annotations

import time
from pathlib import Path

import httpx
import yaml

BASE = "https://api.gios.gov.pl/pjp-api/v1/rest"
CITY_PREFIX = "Warszawa"
POLLUTANTS = {"PM2.5": "pm25", "PM10": "pm10", "NO2": "no2"}
MANUAL_SENSOR_ERROR = "API-ERR-100003"
PAUSE_S = 1.0  # be polite; metadata endpoints are tightly rate-limited
OUT = Path("config/stations.yaml")


def list_payload(body: dict) -> list[dict]:
    """Function to return the Polish 'Lista ...' array from a GIOŚ response."""
    key = next(k for k in body if k.startswith("Lista"))
    return body[key]


def fetch_all(client: httpx.Client, path: str) -> list[dict]:
    """Function to fetch every page of a paginated GIOŚ list endpoint."""
    items: list[dict] = []
    page = 0
    while True:
        r = client.get(f"{BASE}{path}", params={"page": page, "size": 500})
        r.raise_for_status()
        body = r.json()
        items.extend(list_payload(body))
        page += 1
        if page >= body.get("totalPages", 1):
            return items
        time.sleep(PAUSE_S)


def is_hourly_sensor(client: httpx.Client, sensor_id: int) -> bool:
    r = client.get(f"{BASE}/data/getData/{sensor_id}", params={"page": 0, "size": 500})
    if r.status_code == 400 and r.json().get("error_code") == MANUAL_SENSOR_ERROR:
        return False
    r.raise_for_status()
    rows = list_payload(r.json())
    return bool(rows) and rows[0]["Kod stanowiska"].endswith("-1g")


def main() -> None:
    with httpx.Client(timeout=30) as client:
        stations = [
            s
            for s in fetch_all(client, "/station/findAll")
            if s["Nazwa stacji"].startswith(CITY_PREFIX)
        ]
        print(f"Found {len(stations)} {CITY_PREFIX} stations")

        config = []
        for st in stations:
            time.sleep(PAUSE_S)
            sensors = fetch_all(client, f"/station/sensors/{st['Identyfikator stacji']}")
            chosen: dict[str, int] = {}
            for sensor in sensors:
                name = POLLUTANTS.get(sensor["Wskaźnik - wzór"])
                if name is None or name in chosen:
                    continue
                time.sleep(PAUSE_S)
                if is_hourly_sensor(client, sensor["Identyfikator stanowiska"]):
                    chosen[name] = sensor["Identyfikator stanowiska"]

            print(f"  {st['Kod stacji']}: {chosen or 'no hourly sensors'}")
            if chosen:
                config.append(
                    {
                        "id": st["Identyfikator stacji"],
                        "code": st["Kod stacji"],
                        "name": st["Nazwa stacji"],
                        "lat": float(st["WGS84 φ N"]),
                        "lon": float(st["WGS84 λ E"]),
                        "sensors": chosen,
                    }
                )

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(yaml.safe_dump({"stations": config}, allow_unicode=True, sort_keys=False))
    print(f"Wrote {len(config)} stations to {OUT}")


if __name__ == "__main__":
    main()
