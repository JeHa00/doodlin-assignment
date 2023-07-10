from django.contrib.auth import login, logout, authenticate
from django.views.generic import FormView
from django.shortcuts import render
from django.urls import reverse_lazy

from accounts.forms import SignUpForm, LoginForm
from accounts.models import User


def guide_view(request):
    return render(request, "accounts/signup_guide.html")


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        # User
        email = form.data.get("email")
        password = form.data.get("password")
        username = form.data.get("username")
        phone = form.data.get("phone")

        # 유저 생성
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
        )
        user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("guide")

    def form_valid(self, form):
        print("LoginView - form_valid")
        email = form.data.get("email")
        password = form.data.get("password")

        user = authenticate(self.request, username=email, password=password)

        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        print("LoginView - form_invalid")
        return super().form_invalid(form)
