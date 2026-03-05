import random
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from core.form_parser import parse_form


class FormSubmitter:

    def __init__(self, session_manager):
        self.session = session_manager

    def human_delay(self, min_s=1.5, max_s=4.0):
        delay = random.uniform(min_s, max_s)
        print(f"⏳ Esperando {delay:.1f}s...")
        time.sleep(delay)

    def submit(self, target, phone):
        """
        Envía el formulario al target dado.
        Flujo:
          1. GET inicial para verificar conectividad y obtener HTML
          2. Parseo completo del formulario (hidden fields + campos generados)
          3. Inyección del número de teléfono
          4. Delay humano
          5. POST/GET real con los datos del formulario

        Rota proxy solo si el actual falla — no en cada iteración.
        Retorna dict con status_code, o {"status_code": 0} si todo falla.
        """
        url = target["url"]
        method = target.get("method", "POST").upper()
        phone_field = target.get("phone_field", "phone")

        # Número máximo de intentos = tamaño del pool (o 1 si no hay proxies)
        max_attempts = max(len(self.session.proxies_pool), 1)

        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 Intento {attempt}/{max_attempts} — {target['name']}")

            # ── GET inicial ──────────────────────────────────────────────────
            get_response = self.session.get(url)

            if not get_response or get_response.status_code == 0:
                print("⚠ Proxy no conecta, rotando...")
                # BUG FIX: eliminamos el proxy muerto antes de rotar
                self.session.remove_current_proxy()
                self.session.rotate_proxy()
                continue

            # ── Parseo del formulario ────────────────────────────────────────
            # BUG FIX: ahora usamos form_parser.py en lugar de parseo inline
            form_data = parse_form(get_response.text, user_number=phone)

            # Asegurar que el campo teléfono esté presente con el valor correcto
            form_data[phone_field] = phone

            # Resolver action del formulario si existe
            soup = BeautifulSoup(get_response.text, "html.parser")
            form_tag = soup.find("form")
            if form_tag:
                action = form_tag.get("action", "")
                if action and not action.lower().startswith("javascript"):
                    url = urljoin(url, action)

            # ── Delay humano antes del POST ──────────────────────────────────
            self.human_delay()

            # ── Envío real ───────────────────────────────────────────────────
            try:
                if method == "GET":
                    response = self.session.get(url)
                else:
                    response = self.session.post(url, data=form_data)

                if not response or response.status_code == 0:
                    print("⚠ Proxy murió durante el envío, rotando...")
                    self.session.remove_current_proxy()
                    self.session.rotate_proxy()
                    continue

                if response.status_code == 403:
                    backoff = random.uniform(8, 15)
                    print(f"🚫 403 recibido — backoff {backoff:.1f}s")
                    time.sleep(backoff)

                print(f"📨 Respuesta: {response.status_code}")
                return {"status_code": response.status_code}

            except Exception as e:
                print(f"⚠ Excepción durante envío: {e}")
                self.session.remove_current_proxy()
                self.session.rotate_proxy()
                continue

        print("❌ Ningún proxy disponible para este envío.")
        return {"status_code": 0}