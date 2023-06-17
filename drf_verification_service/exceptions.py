

VERIFICATION_NOT_FOUND = 'verification_not_found'


class BaseVerificationException(Exception):
    """
    Base exception for all exceptions in this module.
    """
    def __init__(self, message, code):
        self.message = message
        self.code = code
