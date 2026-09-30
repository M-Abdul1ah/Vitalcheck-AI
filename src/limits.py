import time

MAX_INPUT_CHARS = 500
MAX_REQUESTS = 20
WINDOW_SECONDS = 3600


def check_input_length(text, max_chars=MAX_INPUT_CHARS):
    if len(text) > max_chars:
        return False, f"Message too long ({len(text)} chars). Max is {max_chars}."
    return True, ""


def check_rate_limit(history, max_requests=MAX_REQUESTS, window=WINDOW_SECONDS):
    now = time.time()
    history = [t for t in history if now - t < window]
    if len(history) >= max_requests:
        wait_min = int(window - (now - history[0])) // 60 + 1
        return False, f"Limit reached. Try again in {wait_min} min.", history
    history.append(now)
    return True, "", history
