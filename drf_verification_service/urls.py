from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path(
        "email/send-code/",
        views.EmailSendVerificationCodeView.as_view(),
        name="email_send_code"
    ),
    path(
        "email/verify-code/",
        views.EmailVerifyVerificationCodeView.as_view(),
        name="email_verify_code"
    ),
]
