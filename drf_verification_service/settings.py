def get_email_settings():
    return {
        "code_charset": "0123456789",
        "code_length": 6,
        "code_expiration": 60 * 60 * 24,
    }
