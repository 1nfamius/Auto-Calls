from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urljoin

class FormSubmitter:
    def __init__(self, session_manager):
        self.session = session_manager

    def human_delay(self, min_s=1.5, max_s=4.0):
        time.sleep(random.uniform(min_s, max_s))

    def submit(self, target, phone):
        """Envía el formulario usando proxies rotativos, probando cada proxy antes de POST."""
        url = target["url"]
        method = target.get("method", "POST").upper()

        max_proxy_attempts = len(self.session.proxies_pool)
        for proxy_try in range(max_proxy_attempts):
            self.session.rotate_proxy()
            print(f"🔄 Probando proxy antes de envío (Intento {proxy_try+1}/{max_proxy_attempts})")

            # 🔹 GET test para comprobar que el proxy funciona
            test_response = self.session.get(url)
            if not test_response or getattr(test_response, "status_code", 0) == 0:
                print("⚠ Proxy actual no conecta, rotando a otro...")
                continue  # intentar siguiente proxy

            # -------------------------
            # Preparar datos del formulario
            # -------------------------
            form_data = {}
            soup = BeautifulSoup(test_response.text, "html.parser")
            form = soup.find("form")

            if form:
                # URL action del form
                action = form.get("action")
                if action and not action.lower().startswith("javascript"):
                    url = urljoin(url, action)

                # Extraer hidden
                for hidden in form.find_all("input", {"type": "hidden"}):
                    name = hidden.get("name")
                    value = hidden.get("value", "")
                    if name:
                        form_data[name] = value

            phone_field = target.get("phone_field", "phone")
            form_data[phone_field] = phone
            self.human_delay()

            # -------------------------
            # Enviar formulario real
            # -------------------------
            try:
                if method == "GET":
                    response = self.session.get(url)
                else:
                    response = self.session.post(url, data=form_data)

                if not response or getattr(response, "status_code", 0) == 0:
                    print("⚠ Proxy murió durante POST, rotando a otro...")
                    continue  # intentar otro proxy

                if response.status_code == 403:
                    time.sleep(random.uniform(8, 15))

                return {"status_code": response.status_code}

            except Exception as e:
                print(f"⚠ Error durante submit: {e}")
                continue  # probar siguiente proxy

        # Si ningún proxy funciona
        print("❌ Ningún proxy disponible para este envío.")
        return {"status_code": 0}