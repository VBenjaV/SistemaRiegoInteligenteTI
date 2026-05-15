#!/usr/bin/env python3
"""Simulador de sensor para probar API de lecturas."""

import argparse
import os
import random
import time
from datetime import datetime, timezone
from typing import Optional

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulador de lecturas de sensor")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "http://localhost:8000"))
    parser.add_argument("--device-id", default="sensor1")
    parser.add_argument("--interval", type=float, default=5.0, help="Segundos entre lecturas")
    parser.add_argument("--count", type=int, default=0, help="Numero de lecturas (0 = infinito)")
    parser.add_argument("--hum-min", type=float, default=20.0)
    parser.add_argument("--hum-max", type=float, default=80.0)
    parser.add_argument("--temp-min", type=float, default=15.0)
    parser.add_argument("--temp-max", type=float, default=30.0)
    parser.add_argument("--no-temp", action="store_true", help="No enviar temperatura")
    parser.add_argument("--include-timestamp", action="store_true")
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> dict:
    humedad = round(random.uniform(args.hum_min, args.hum_max), 2)
    payload = {
        "humedad": humedad,
        "dispositivo_id": args.device_id,
    }

    if not args.no_temp:
        temperatura = round(random.uniform(args.temp_min, args.temp_max), 2)
        payload["temperatura"] = temperatura

    if args.include_timestamp:
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()

    return payload


def post_reading(base_url: str, payload: dict) -> Optional[dict]:
    url = f"{base_url.rstrip('/')}/api/sensores/"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    args = parse_args()
    sent = 0

    while True:
        payload = build_payload(args)
        try:
            result = post_reading(args.base_url, payload)
            print(f"OK lectura id={result.get('id')} humedad={payload['humedad']}%")
        except requests.RequestException as exc:
            print(f"ERROR envio lectura: {exc}")

        sent += 1
        if args.count and sent >= args.count:
            break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
