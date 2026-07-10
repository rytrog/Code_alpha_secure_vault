import time
from collections import defaultdict
from ..config import settings
from ..constants import RATE_LIMIT_WINDOW


class RateLimiter:
    def __init__(self):
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = RATE_LIMIT_WINDOW

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        # Clean old entries
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        if len(self.requests[key]) >= self.limit:
            return False
        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        now = time.time()
        window_start = now - self.window
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        return max(0, self.limit - len(self.requests[key]))

    def reset(self, key: str):
        self.requests.pop(key, None)

    def get_retry_after(self, key: str) -> int:
        if not self.requests[key]:
            return 0
        oldest = min(self.requests[key])
        return max(0, int(self.window - (time.time() - oldest)))


rate_limiter = RateLimiter()
