import json
import csv
from datetime import datetime
from time import sleep
from core.session_manager import SessionManager
from core.submitter import FormSubmitter

RETRIES = 3       # Número de intentos por target
DELAY = 2         # Segundos entre reintentos

# Pedir número al usuario
while True:
    PHONE = input("Introduce el número de teléfono (máx. 9 dígitos): ").strip()
    if PHONE.isdigit() and len(PHONE) == 9:
        break
    print("Número inválido. Debe contener solo dígitos y como máximo 9 números.")

# Cargar targets
with open("config.json") as f:
    config = json.load(f)
    targets = config.get("targets", [])

# Inicializar sesiones y submitter
session_manager = SessionManager()
submitter = FormSubmitter(session_manager)

# Preparar CSV para logs
csv_file = "submission_log.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "target", "status", "http_code", "attempt"])

# Contadores finales
success_count = 0
fail_count = 0

for target in targets:
    for attempt in range(1, RETRIES + 1):
        try:
            result = submitter.submit(target, PHONE)

            # Si la petición falló completamente
            if result is None:
                print(f"❌ {target['name']} -> ERROR en la petición (Intento {attempt}/{RETRIES})")
                sleep(DELAY)
                continue

            code = result.get("status_code", 0)

            # Aviso en tiempo real
            if code == 200:
                print(f"✅ {target['name']} -> Enviado con éxito (Intento {attempt}/{RETRIES})")
                success_count += 1
            else:
                print(f"⚠ {target['name']} -> Respondió con código {code} (Intento {attempt}/{RETRIES})")

            # Guardar log en CSV
            timestamp = datetime.now().isoformat()
            with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, target["name"], "VÁLIDO" if code == 200 else "NO VÁLIDO", code, attempt])

            # Si fue exitoso, no hace falta reintentar
            if code == 200:
                break
            else:
                sleep(DELAY)

        except Exception as e:
            print(f"❌ {target['name']} -> FALLO inesperado: {e} (Intento {attempt}/{RETRIES})")
            sleep(DELAY)
            continue

    else:
        # Si agotó los intentos
        fail_count += 1
        print(f"❌ {target['name']} -> No se pudo enviar después de {RETRIES} intentos")

# Resumen final
print("\n📊 Resumen final:")
print(f"✅ Enviados con éxito: {success_count}")
print(f"⚠ No válidos/fallidos: {fail_count}")
print(f"Logs guardados en: {csv_file}")
