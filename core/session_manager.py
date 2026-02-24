import requests
import random
from urllib.parse import urlparse

class SessionManager:
    def __init__(self, proxies=None):
        if not proxies:
            raise Exception("Este modo requiere proxies. No hay proxies disponibles.")
        self.proxies_pool = proxies.copy()
        self.current_proxy = None

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        ]

        self.session = self.create_session()

    def create_session(self):
        if not self.proxies_pool:
            raise Exception("No quedan proxies funcionales.")

        session = requests.Session()
        user_agent = random.choice(self.user_agents)
        session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document"
        })

        available_proxies = [p for p in self.proxies_pool if p != self.current_proxy]
        if not available_proxies:
            available_proxies = self.proxies_pool

        self.current_proxy = random.choice(available_proxies)
        print(f"🔐 Usando proxy: {self.current_proxy['http']}")
        session.proxies.update(self.current_proxy)
        return session

    def rotate_proxy(self):
        self.session.close()
        self.session = self.create_session()

    def warmup(self, url):
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}/"
            self.session.get(base_url, timeout=10)
            return True
        except:
            return False

    def get(self, url, timeout=15):
        return self._request("get", url, timeout=timeout)

    def post(self, url, data=None, timeout=15):
        return self._request("post", url, data=data, timeout=timeout)

    def _request(self, method, url, data=None, timeout=15):
        try:
            if method == "post":
                self.warmup(url)
            if method == "get":
                return self.session.get(url, timeout=timeout)
            else:
                return self.session.post(url, data=data, timeout=timeout)
        except requests.RequestException as e:
            print("⚠ Error de conexión con proxy.")
            class FakeResponse:
                def __init__(self, error):
                    self.status_code = 0
                    self.text = str(error)
            return FakeResponse(e)