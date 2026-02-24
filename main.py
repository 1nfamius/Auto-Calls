import json
import csv
from datetime import datetime
from time import sleep

from core.session_manager import SessionManager
from core.submitter import FormSubmitter
from core.proxy_manager import load_proxies, build_priority_pool, build_working_proxy_pool

RETRIES = 3
DELAY = 2

# -------------------------
# Preguntar si usar proxies
# -------------------------
def ask_proxy_mode():
    while True:
        choice = input("¿Usar proxies? (s/n): ").strip().lower()

        if choice in ["s", "si", "sí"]:
            return True
        elif choice in ["n", "no"]:
            return False
        else:
            print("Respuesta no válida. Usa 's' o 'n'.")


use_proxies = ask_proxy_mode()

working_proxies = []

# -------------------------
# Cargar proxies solo si se elige
# -------------------------
if use_proxies:
    print("🔎 Cargando y verificando proxies...")

    socks5, https_list, http_list, socks4 = load_proxies("proxies.txt")
    priority_proxies = build_priority_pool(socks5, https_list, http_list, socks4)
    working_proxies = build_working_proxy_pool(priority_proxies)

    if not working_proxies:
        print("❌ No hay proxies funcionales. Continuando sin proxy.")
    else:
        print(f"✅ Proxies funcionales: {len(working_proxies)}")

# -------------------------
# Crear sesión
# -------------------------
session_manager = SessionManager(proxies=working_proxies)
submitter = FormSubmitter(session_manager)

# -------------------------
# Pedir número
# -------------------------
while True:
    PHONE = input("Introduce el número de teléfono (9 dígitos exactos): ").strip()
    if PHONE.isdigit() and len(PHONE) == 9:
        break
    print("Número inválido. Debe contener exactamente 9 dígitos.")

# -------------------------
# Cargar targets
# -------------------------
with open("config.json") as f:
    config = json.load(f)
    targets = config.get("targets", [])

# -------------------------
# Preparar CSV
# -------------------------
csv_file = "submission_log.csv"

with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "target", "status", "http_code", "attempt"])

success_count = 0
fail_count = 0

# -------------------------
# Envíos
# -------------------------
for target in targets:
    for attempt in range(1, RETRIES + 1):
        result = submitter.submit(target, PHONE)

        if result is None:
            print(f"❌ {target['name']} -> Error en petición (Intento {attempt}/{RETRIES})")
            sleep(DELAY)
            continue

        code = result.get("status_code", 0)

        if code == 200:
            print(f"✅ {target['name']} -> Enviado (Intento {attempt}/{RETRIES})")
            success_count += 1
        else:
            print(f"⚠ {target['name']} -> Código {code} (Intento {attempt}/{RETRIES})")

        timestamp = datetime.now().isoformat()

        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                target["name"],
                "VÁLIDO" if code == 200 else "NO VÁLIDO",
                code,
                attempt
            ])

        if code == 200:
            break

        sleep(DELAY)

    else:
        fail_count += 1
        print(f"❌ {target['name']} -> Falló tras {RETRIES} intentos")

# -------------------------
# Resumen final
# -------------------------
print("\n📊 Resumen final:")
print(f"✅ Éxitos: {success_count}")
print(f"⚠ Fallidos: {fail_count}")
print(f"Logs guardados en: {csv_file}")
