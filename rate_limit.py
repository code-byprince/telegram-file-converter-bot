import time
import threading
from collections import defaultdict, deque

MAX_REQUESTS = 5       # ek window me max kitni files allow hain
WINDOW_SECONDS = 60    # window ka size (seconds me)

_history = defaultdict(deque)
_lock = threading.Lock()


def check_rate_limit(user_id: int):
    """
    True, 0 return karta hai agar allowed hai.
    False, wait_seconds return karta hai agar limit cross ho gayi.
    """
    now = time.time()
    with _lock:
        q = _history[user_id]
        while q and now - q[0] > WINDOW_SECONDS:
            q.popleft()

        if len(q) >= MAX_REQUESTS:
            wait = int(WINDOW_SECONDS - (now - q[0])) + 1
            return False, wait

        q.append(now)
        return True, 0
