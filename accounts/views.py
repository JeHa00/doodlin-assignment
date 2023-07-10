from django.views.generic import FormView
from django.urls import reverse_lazy

from accounts.forms import SignUpForm
from accounts.models import User


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
