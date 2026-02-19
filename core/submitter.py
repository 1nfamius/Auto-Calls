from core.form_parser import parse_form
import time

class FormSubmitter:
    def __init__(self, session_manager):
        self.session = session_manager

    def submit(self, target, user_number=None):
        r = self.session.get(target["url"])
        form_data = parse_form(r.text, user_number)

        time.sleep(1.2)  # delay simulación humana
        response = self.session.post(target["url"], form_data)

        return {"status_code": response.status_code, "response": response.text}
