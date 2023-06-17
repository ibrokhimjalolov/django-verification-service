from django.dispatch import Signal


email_verification_send = Signal()
sms_verification_send = Signal()


email_verification_confirm = Signal()
sms_verification_confirm = Signal()
