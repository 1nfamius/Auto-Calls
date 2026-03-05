import json
from time import sleep

from core.session_manager import SessionManager
from core.submitter import FormSubmitter
from core.proxy_manager import load_proxies, build_priority_pool, build_working_proxy_pool
from core.logger import init_csv, log_submission, log_info, log_error

RETRIES = 3
DELAY = 2


# ─────────────────────────────────────────────
# Cargar config primero (necesaria para credenciales Webshare)
# ─────────────────────────────────────────────
with open("config.json") as f:
    config = json.load(f)

targets = config.get("targets", [])


# ─────────────────────────────────────────────
# Modo proxy
# ─────────────────────────────────────────────
def ask_proxy_mode():
    while True:
        choice = input("¿Usar proxies? (s/n): ").strip().lower()
        if choice in ("s", "si", "sí"):
            return True
        elif choice in ("n", "no"):
            return False
        print("Respuesta no válida. Usa 's' o 'n'.")


use_proxies = ask_proxy_mode()
working_proxies = []

if use_proxies:
    print("\n🔎 Cargando y verificando proxies...")

    # Leer credenciales Webshare desde config.json
    webshare_cfg = config.get("webshare", {})
    ws_user = ws_pass = None

    if webshare_cfg.get("enabled"):
        ws_user = webshare_cfg.get("username")
        ws_pass = webshare_cfg.get("password")
        print(f"🔑 Webshare habilitado — usuario: {ws_user}")
    else:
        print("🌐 Webshare deshabilitado — usando proxies sin autenticación")

    socks5, https_list, http_list, socks4 = load_proxies(
        "proxies.txt", username=ws_user, password=ws_pass
    )
    priority_pool = build_priority_pool(socks5, https_list, http_list, socks4)
    working_proxies = build_working_proxy_pool(priority_pool)

    if not working_proxies:
        print("⚠ No hay proxies funcionales. Continuando en modo directo.")
    else:
        print(f"✅ Proxies funcionales: {len(working_proxies)}\n")


# ─────────────────────────────────────────────
# Sesión y submitter
# ─────────────────────────────────────────────
session_manager = SessionManager(proxies=working_proxies)
submitter = FormSubmitter(session_manager)


# ─────────────────────────────────────────────
# Número de teléfono
# ─────────────────────────────────────────────
while True:
    PHONE = input("Introduce el número de teléfono (9 dígitos exactos): ").strip()
    if PHONE.isdigit() and len(PHONE) == 9:
        break
    print("❌ Número inválido. Debe contener exactamente 9 dígitos.")


# ─────────────────────────────────────────────
# Inicializar logging y mostrar targets
# ─────────────────────────────────────────────
init_csv()
print(f"\n📋 Targets cargados: {len(targets)}")

success_count = 0
fail_count = 0


# ─────────────────────────────────────────────
# Envíos
# ─────────────────────────────────────────────
for target in targets:
    target_success = False

    for attempt in range(1, RETRIES + 1):
        result = submitter.submit(target, PHONE)
        code = result.get("status_code", 0)

        log_submission(target["name"], code, attempt)

        if code == 200:
            print(f"✅ {target['name']} → Enviado OK (intento {attempt}/{RETRIES})")
            success_count += 1
            target_success = True
            break
        else:
            print(f"⚠ {target['name']} → Código {code} (intento {attempt}/{RETRIES})")
            sleep(DELAY)

    if not target_success:
        fail_count += 1
        log_error(f"{target['name']} falló tras {RETRIES} intentos")
        print(f"❌ {target['name']} → Falló tras {RETRIES} intentos")


# ─────────────────────────────────────────────
# Resumen
# ─────────────────────────────────────────────
print("\n" + "─" * 40)
print("📊 Resumen final:")
print(f"   ✅ Éxitos  : {success_count}")
print(f"   ❌ Fallidos: {fail_count}")
print(f"   📁 Logs    : submission_log.csv / submission_log.txt")
print("─" * 40)