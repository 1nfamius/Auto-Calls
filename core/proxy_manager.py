import requests

VALIDATION_TIMEOUT = 15
TEST_URL = "https://ipv4.webshare.io/"  # Webshare tiene endpoint propio para verificar IP


def _build_proxy_url(raw, username=None, password=None):
    """
    Construye la URL completa de un proxy inyectando credenciales si se proporcionan.

    Casos soportados:
      - "ip:port"                  → http://user:pass@ip:port  (Webshare sin esquema)
      - "http://ip:port"           → http://user:pass@ip:port
      - "http://user:pass@ip:port" → se usa tal cual (ya tiene credenciales)
      - "socks5://ip:port"         → socks5h://user:pass@ip:port
      - "socks4://ip:port"         → socks4://user:pass@ip:port

    Retorna la URL lista para usar en requests.
    """
    has_auth = "@" in raw  # ya tiene credenciales embebidas

    # Detectar esquema
    if raw.startswith("socks5://"):
        scheme = "socks5h"
        host = raw.replace("socks5://", "").replace("socks5h://", "")
    elif raw.startswith("socks4://"):
        scheme = "socks4"
        host = raw.replace("socks4://", "")
    elif raw.startswith("https://"):
        scheme = "https"
        host = raw.replace("https://", "")
    elif raw.startswith("http://"):
        scheme = "http"
        host = raw.replace("http://", "")
    else:
        # Sin esquema → Webshare usa HTTP
        scheme = "http"
        host = raw

    if has_auth or not (username and password):
        # Ya tiene credenciales o no se proporcionaron → devolver con esquema correcto
        return f"{scheme}://{host}"

    return f"{scheme}://{username}:{password}@{host}"


def load_proxies(file_path, username=None, password=None):
    """
    Carga proxies desde archivo de texto e inyecta credenciales si se pasan.

    Formato soportado en proxies.txt:
      - ip:port                    (Webshare / genérico sin esquema)
      - http://ip:port
      - socks5://ip:port
      - http://user:pass@ip:port   (credenciales ya embebidas)

    Retorna 4 listas separadas por tipo: (socks5, https, http, socks4)
    """
    socks5, https_list, http_list, socks4 = [], [], [], []

    with open(file_path, "r") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#"):
                continue

            url = _build_proxy_url(raw, username, password)

            if url.startswith("socks5"):
                socks5.append(url)
            elif url.startswith("socks4"):
                socks4.append(url)
            elif url.startswith("https"):
                https_list.append(url)
            else:
                http_list.append(url)

    return socks5, https_list, http_list, socks4


def build_priority_pool(socks5, https_list, http_list, socks4):
    """
    Combina en un pool ordenado por prioridad: SOCKS5 > HTTPS > HTTP > SOCKS4.
    Retorna lista de dicts {http: ..., https: ...} listos para requests.
    """
    ordered = socks5 + https_list + http_list + socks4
    return [{"http": p, "https": p} for p in ordered]


def validate_proxy(proxy_dict, timeout=VALIDATION_TIMEOUT):
    """
    Valida un proxy contra el endpoint de Webshare (devuelve la IP saliente).
    Retorna True si responde con status 200.
    """
    try:
        r = requests.get(TEST_URL, proxies=proxy_dict, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def build_working_proxy_pool(proxy_list):
    """
    Filtra el pool validando cada proxy. Retorna solo los funcionales.
    Muestra la IP saliente confirmada por Webshare si la validación pasa.
    """
    working = []
    total = len(proxy_list)

    for i, proxy in enumerate(proxy_list, 1):
        addr = proxy.get("http", "?")
        # Ocultar credenciales en el log: mostrar solo host:port
        display = addr.split("@")[-1] if "@" in addr else addr
        print(f"[{i}/{total}] Validando {display}...", end=" ", flush=True)

        try:
            r = requests.get(TEST_URL, proxies=proxy, timeout=VALIDATION_TIMEOUT)
            if r.status_code == 200:
                print(f"✅ IP saliente: {r.text.strip()}")
                working.append(proxy)
            else:
                print(f"❌ Status {r.status_code}")
        except Exception as e:
            print(f"❌ {e}")

    return working


def clean_proxies_file(file_path, username=None, password=None):
    """
    Utilidad de mantenimiento: reescribe proxies.txt conservando solo los válidos.
    Guarda solo ip:port (sin credenciales) para mantener el archivo limpio.
    """
    valid_raw = []

    with open(file_path, "r") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    for raw in lines:
        url = _build_proxy_url(raw, username, password)
        proxy_dict = {"http": url, "https": url}
        display = raw.split("@")[-1] if "@" in raw else raw
        print(f"🔎 Probando {display}...", end=" ", flush=True)

        if validate_proxy(proxy_dict):
            # Guardar solo ip:port original (sin credenciales)
            valid_raw.append(raw.split("@")[-1] if "@" in raw else raw)
            print("✅")
        else:
            print("❌ eliminado")

    with open(file_path, "w") as f:
        f.write("\n".join(valid_raw) + "\n")

    print(f"\n✅ Proxies válidos conservados: {len(valid_raw)}/{len(lines)}")
    return valid_raw