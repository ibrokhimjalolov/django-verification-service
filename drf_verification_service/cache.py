from datetime import datetime

from django.core.cache import cache
from . import exceptions


class VerificationObject:
    created_at: datetime
    uuid: str
    attempts: int

    def __init__(self, uuid):
        self.uuid = uuid
        if not self.exists():
            raise exceptions.BaseVerificationException("Invalid verification key", exceptions.VERIFICATION_NOT_FOUND)

    def exists(self):
        cache_key = self.get_cache_key()
        data = cache.get(cache_key, {})
        self.created_at = data.get('created_at', None)
        if self.created_at and (datetime.now() - self.created_at).total_seconds() > 60*60*24:
            cache.delete(cache_key)
            return False
        self.attempts = data.get('attempts', None)
        return bool(data)

    def get_cache_key(self):
        return f"verification-{self.uuid}"

    def save(self, data):
        cache_key = self.get_cache_key()
        cache.set(cache_key, data, timeout=60*60*24*7)
