import datetime

def log_result(target_name, result):
    timestamp = datetime.datetime.now().isoformat()
    status = result["status_code"]
    success = "VÁLIDO" if status == 200 else "NO VÁLIDO"
    print(f"[{timestamp}] {target_name} -> {status} ({success})")
