from django.contrib.auth.decorators import login_required
from django.urls import path

from accounts import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("guide/", login_required(views.guide_view), name="guide"),
]
