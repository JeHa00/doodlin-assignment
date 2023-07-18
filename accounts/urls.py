from django.views.generic import RedirectView
from django.urls import path

from accounts import views

urlpatterns = [
    path("", RedirectView.as_view(url="/login")),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("accounts/signup-list/", views.SignupListView.as_view(), name="signup_list"),
    path(
        "accounts/signup-list/<int:user_id>",
        views.SignupDetailView.as_view(),
        name="signup_detail",
    ),
    path("employees/", views.EmployeeListView.as_view(), name="employee_list"),
    path(
        "employees/<int:employee_id>",
        views.EmployeeDetailView.as_view(),
        name="employee_detail",
    ),
    path("guide/", views.guide_view, name="guide"),
]
