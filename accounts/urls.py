from django.urls import path

from accounts import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("accounts/signup-list/", views.SignupListView.as_view(), name="signup_list"),
    path(
        "accounts/signup-list/<int:user_id>",
        views.signup_user_detail_view,
        name="signup_detail",
    ),
    path("guide/", views.guide_view, name="guide"),
    path("employees/", views.EmployeeListView.as_view(), name="employee_list"),
]
