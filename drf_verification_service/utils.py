import logging
from dataclasses import dataclass, asdict
from django.core.cache import cache as _cache

from . import exceptions


def get_cache():
    return _cache


@dataclass
class VerificationData:
    id: str
    secret: str
    code: str
    attempt: int
    verified: bool

    @classmethod
    def retrieve(cls, id, secret):
        cache = get_cache()
        key = cls.get_key(id, secret)
        data = cache.get(key)
        if data:
            return cls(**data)
        raise exceptions.BaseVerificationException("Invalid verification id, secret", exceptions.VERIFICATION_NOT_FOUND)

    @classmethod
    def delete(cls, id, secret):
        cache = get_cache()
        key = cls.get_key(id, secret)
        cache.delete(key)

    def save_state(self, expire=None):
        cache = get_cache()
        key = self.get_key(self.id, self.secret)
        cache.set(key, asdict(self), expire)
        logging.debug(f"EmailVerification.save_state: {self}")

    @classmethod
    def get_key(cls, id, secret):
        return f"drf-verification-service:{id}:{secret}"


def get_verification_data(id, secret):
    return VerificationData.retrieve(id, secret)
