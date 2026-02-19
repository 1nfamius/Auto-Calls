import json
from core.session_manager import SessionManager
from core.submitter import FormSubmitter
from core.logger import log_result

PHONE = "600123456"

# Cargar targets desde JSON
with open("config.json") as f:
    targets = json.load(f)

session_manager = SessionManager()
submitter = FormSubmitter(session_manager)

for target in targets:
    result = submitter.submit(target, PHONE)
    log_result(target["name"], result)
