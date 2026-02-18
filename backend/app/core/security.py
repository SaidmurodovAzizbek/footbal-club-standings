from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Rate limiter - IP address bo'yicha cheklash
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])
