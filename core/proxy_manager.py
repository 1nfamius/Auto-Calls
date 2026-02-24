import requests

def load_proxies(file_path):
    socks5 = []
    https = []
    http = []
    socks4 = []

    with open(file_path, "r") as f:
        for line in f:
            proxy = line.strip()
            if not proxy:
                continue

            if proxy.startswith("socks5://"):
                socks5.append(proxy.replace("socks5://", "socks5h://"))

            elif proxy.startswith("socks4://"):
                socks4.append(proxy)

            elif proxy.startswith("https://"):
                https.append(proxy)

            elif proxy.startswith("http://"):
                http.append(proxy)

            else:
                # Si no tiene esquema asumimos SOCKS5
                socks5.append(f"socks5h://{proxy}")

    return socks5, https, http, socks4

def build_priority_pool(socks5, https, http, socks4):
    ordered = []

    # Prioridad real
    ordered.extend(socks5)
    ordered.extend(https)
    ordered.extend(http)
    ordered.extend(socks4)

    proxies = []
    for proxy in ordered:
        proxies.append({
            "http": proxy,
            "https": proxy
        })

    return proxies


TEST_URL = "https://www.google.com"
TIMEOUT = 8

def validate_proxy(proxy_dict):
    try:
        r = requests.get(TEST_URL, proxies=proxy_dict, timeout=TIMEOUT)
        if r.status_code == 200:
            return True
        return False
    except:
        return False
    

def clean_proxies_file(file_path):
    valid_proxies = []

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        proxy = line.strip()
        proxy_dict = {
            "http": proxy,
            "https": proxy
        }

        print(f"🔎 Probando {proxy}...")
        if validate_proxy(proxy_dict):
            valid_proxies.append(proxy)
            print("✅ OK")
        else:
            print("❌ Eliminado")

    # Sobrescribimos el archivo solo con los válidos
    with open(file_path, "w") as f:
        for proxy in valid_proxies:
            f.write(proxy + "\n")

    print(f"\nProxies funcionales: {len(valid_proxies)}")


def build_working_proxy_pool(proxy_list):
    working = []

    for proxy in proxy_list:
        if validate_proxy(proxy):
            print(f"[✔] Proxy válido: {proxy['http']}")
            working.append(proxy)
        else:
            print(f"[✘] Proxy muerto: {proxy['http']}")

    return working

