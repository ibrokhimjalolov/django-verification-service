import random
from uuid import uuid4
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .settings import get_email_settings
from .utils import get_verification_data, VerificationData
from . import signals
from . import exceptions


class EmailSendVerificationCodeView(APIView):
    """
    Send verification code to email
    """

    errors = {
        "email_not_found": "Email not found",
        "email_not_verified": "Email not verified",
        "email_cant_send": "Email can't send",
    }

    def __init__(self, *args, **kwargs):
        self.email_settings = get_email_settings()
        super().__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        validated_data = {"email": request.data.get("email"), "uuid": uuid4().hex, "code": self.generate_code()}
        try:
            email_verification = VerificationData(
                id=validated_data["email"],
                secret=validated_data["uuid"],
                code=validated_data["code"],
                attempt=0,
                verified=False
            )
            email_verification.save_state(expire=self.email_settings["code_expiration"])
            signals.email_verification_send.send(sender=self.__class__, data=validated_data)
        except exceptions.BaseVerificationException as e:
            response = {
                "success": False,
                "error_code": e.code,
                "error_message": e.message,
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "success": True,
            "email": validated_data["email"],
            "uuid": validated_data["uuid"],
        }
        return Response(response, status=status.HTTP_200_OK)

    def generate_code(self):
        return "".join(random.choices(
            self.email_settings["code_charset"],
            k=self.email_settings["code_length"]
        ))


class EmailVerifyVerificationCodeView(APIView):
    """
    Send verification code to email
    """

    errors = {
        "email_invalid_code": "Invalid code",
        "email_not_found": "Email not found",
        "email_already_verified": "Email already verified",
    }

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            self.verify_verification_code(data, raise_exception=True)
            signals.email_verification_confirm.send(sender=self.__class__, data=data)
        except exceptions.BaseVerificationException as ex:
            response = {
                "success": False,
                "error_code": ex.code,
                "error_message": ex.message,
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            "success": True,
            "email": data["email"],
        }
        return Response(response, status=status.HTTP_200_OK)

    def verify_verification_code(self, validated_data, raise_exception=False):
        email_settings = get_email_settings()
        email_verification = get_verification_data(validated_data["email"], validated_data["uuid"])
        if not email_verification:
            self.fail("email_not_found")
        if email_verification.verified:
            self.fail("email_already_verified")
        if email_verification.attempt >= email_settings["attempt_limit"]:
            email_verification.delete(email_verification.email, email_verification.uuid)
            self.fail("email_not_found")
        if email_verification.code != validated_data["code"]:
            email_verification.attempt += 1
            email_verification.save_state()
            self.fail("email_invalid_code")
        email_verification.verified = True
        email_verification.save_state()

    def fail(self, code):
        raise exceptions.BaseVerificationException(self.errors[code], code=code)
