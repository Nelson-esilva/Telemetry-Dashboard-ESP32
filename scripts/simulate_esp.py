#!/usr/bin/env python3
"""Simula o envio de telemetria do ESP32 via HTTP POST."""

import random
import sys
import time
from datetime import datetime

import requests

API_URL = "http://localhost:8000/telemetry"
DEVICE_ID = "linha_01"
INTERVAL_SECONDS = 5

STATUS_OPTIONS = [
    ("RUNNING", 85),
    ("IDLE", 10),
    ("ALARM", 5),
]


def pick_status() -> str:
    roll = random.randint(1, 100)
    cumulative = 0
    for status, weight in STATUS_OPTIONS:
        cumulative += weight
        if roll <= cumulative:
            return status
    return "RUNNING"


def generate_payload(pecas: int) -> dict:
    pecas += random.randint(0, 3)
    return {
        "device_id": DEVICE_ID,
        "pecas_produzidas": pecas,
        "temperatura_c": round(random.uniform(25.0, 75.0), 1),
        "rpm_motor": random.randint(800, 1500),
        "status_maquina": pick_status(),
        "tempo_ciclo_s": round(random.uniform(1.5, 4.0), 1),
        "eficiencia_pct": round(random.uniform(85.0, 99.0), 1),
    }, pecas


def main() -> None:
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    else:
        api_url = API_URL

    print(f"Simulador ESP32 — enviando para {api_url} a cada {INTERVAL_SECONDS}s")
    print("Pressione Ctrl+C para parar.\n")

    pecas = 0
    while True:
        payload, pecas = generate_payload(pecas)
        try:
            response = requests.post(api_url, json=payload, timeout=5)
            response.raise_for_status()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] OK {response.status_code} — {payload}")
        except requests.RequestException as exc:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRO — {exc}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
