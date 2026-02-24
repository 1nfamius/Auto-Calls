import datetime

def log_submission(target, response):
    status = response.status_code if response else "NO_RESPONSE"

    with open("submission_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{target} | {status}\n")