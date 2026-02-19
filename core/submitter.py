from bs4 import BeautifulSoup

class FormSubmitter:
    def __init__(self, session_manager):
        self.session = session_manager

    def submit(self, target, phone):
        url = target["url"]
        method = target.get("method", "POST").upper()

        try:
            # Si es GET simple
            if method == "GET":
                response = self.session.get(url)
                if response is None:
                    return None

            # Si es POST con posible token
            else:
                # 1️⃣ GET inicial para cookies y posibles tokens
                initial_response = self.session.get(url)
                if initial_response is None:
                    return None

                soup = BeautifulSoup(initial_response.text, "html.parser")

                # 2️⃣ Intentar encontrar token (si existe)
                token_input = soup.find("input", {"name": "csrf_token"})
                token = token_input.get("value") if token_input else None

                # 3️⃣ Preparar datos
                form_data = {
                    "phone": phone
                }

                if token:
                    form_data["csrf_token"] = token

                # 4️⃣ Enviar POST
                response = self.session.post(url, data=form_data)
                if response is None:
                    return None

            return {
                "status_code": response.status_code
            }

        except Exception as e:
            print(f"Error en submit(): {e}")
            return None
