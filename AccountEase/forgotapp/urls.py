from django.urls import path
from . import views

app_name = "forgotapp"

urlpatterns = [
    path("forgot-pswd/", views.forgot_password, name="forgot_pswd"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
]
