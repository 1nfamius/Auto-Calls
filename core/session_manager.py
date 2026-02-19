import requests

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",

        })

    def get(self, url, timeout=15):
        try:
            return self.session.get(url, timeout=timeout)
        except requests.RequestException as e:
            print(f"GET fallo en {url}: {e}")
            return None

    def post(self, url, data=None, timeout=15):
        try:
            return self.session.post(url, data=data, timeout=timeout, stream=False)
        except requests.RequestException as e:
            print(f"POST fallo en {url}: {e}")
            return None
