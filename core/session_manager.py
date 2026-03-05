import requests
import random
from urllib.parse import urlparse


class SessionManager:

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    ]

    def __init__(self, proxies=None):
        # BUG FIX: ya no lanza excepción — modo sin proxy soportado
        self.use_proxies = bool(proxies)
        self.proxies_pool = proxies.copy() if proxies else []
        self.current_proxy = None
        self.session = self._create_session()

    def _create_session(self):
        """Crea una sesión HTTP con headers realistas y proxy asignado si corresponde."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        })

        if self.use_proxies and self.proxies_pool:
            available = [p for p in self.proxies_pool if p != self.current_proxy]
            if not available:
                available = self.proxies_pool  # si solo hay uno, reutilizarlo

            self.current_proxy = random.choice(available)
            session.proxies.update(self.current_proxy)
            print(f"🔐 Proxy asignado: {self.current_proxy['http']}")
        else:
            print("🌐 Modo directo (sin proxy)")

        return session

    def rotate_proxy(self):
        """Cierra la sesión actual y crea una nueva con un proxy diferente."""
        if not self.use_proxies:
            # Sin proxies, solo renovamos la sesión (nuevo User-Agent, cookies limpias)
            self.session.close()
            self.session = self._create_session()
            return

        if len(self.proxies_pool) == 0:
            print("⚠ Pool de proxies vacío, no se puede rotar.")
            return

        self.session.close()
        self.session = self._create_session()

    def remove_current_proxy(self):
        """Elimina el proxy actual del pool (proxy muerto confirmado)."""
        if self.current_proxy and self.current_proxy in self.proxies_pool:
            print(f"🗑 Eliminando proxy muerto: {self.current_proxy['http']}")
            self.proxies_pool.remove(self.current_proxy)
            self.current_proxy = None

    def warmup(self, url, timeout=10):
        """
        Realiza una petición GET a la raíz del dominio para establecer cookies
        y simular navegación orgánica antes de un POST.
        Retorna True si el warmup fue exitoso.
        """
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}/"
            r = self.session.get(base_url, timeout=timeout)
            return r.status_code < 500
        except requests.RequestException as e:
            print(f"⚠ Warmup fallido: {e}")
            return False

    def get(self, url, timeout=15):
        return self._request("get", url, timeout=timeout)

    def post(self, url, data=None, timeout=15):
        return self._request("post", url, data=data, timeout=timeout)

    def _request(self, method, url, data=None, timeout=15):
        """
        Ejecuta la petición HTTP.
        Retorna un FakeResponse con status_code=0 si hay error de conexión,
        en lugar de lanzar excepción — permite al caller decidir cómo actuar.
        """
        try:
            if method == "get":
                return self.session.get(url, timeout=timeout)
            elif method == "post":
                return self.session.post(url, data=data, timeout=timeout)
        except requests.RequestException as e:
            print(f"⚠ Error de conexión: {e}")
            return _FakeResponse(error=e)


class _FakeResponse:
    """Respuesta simulada para errores de red, evita None checks en el caller."""
    def __init__(self, error=None):
        self.status_code = 0
        self.text = str(error) if error else ""
        self.ok = False