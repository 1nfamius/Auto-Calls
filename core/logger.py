import datetime
import csv
import os

LOG_TXT = "submission_log.txt"
LOG_CSV = "submission_log.csv"


def init_csv():
    """Inicializa el CSV con cabeceras si no existe."""
    if not os.path.exists(LOG_CSV):
        with open(LOG_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "target", "status", "http_code", "attempt"])


def log_submission(target_name, status_code, attempt):
    """
    BUG FIX: logger.py ahora se usa realmente desde main.py.
    Registra el resultado de un envío en ambos formatos: .txt y .csv.
    """
    timestamp = datetime.datetime.now().isoformat()
    status_label = "VÁLIDO" if status_code == 200 else "NO VÁLIDO"

    # Log texto plano
    with open(LOG_TXT, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {target_name} | {status_label} | HTTP {status_code} | Intento {attempt}\n")

    # Log CSV
    with open(LOG_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, target_name, status_label, status_code, attempt])


def log_info(message):
    """Log de mensaje informativo general."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] ℹ {message}")
    with open(LOG_TXT, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] INFO: {message}\n")


def log_error(message):
    """Log de error."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] ❌ {message}")
    with open(LOG_TXT, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ERROR: {message}\n")