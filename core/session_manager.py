import requests

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 BotTester/1.0"
        })

    def get(self, url):
        return self.session.get(url)

    def post(self, url, data):
        return self.session.post(url, data=data)
