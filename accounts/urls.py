from django.urls import path

from accounts import views

urlpatterns = [
    path("accounts/signup/", views.SignUpView.as_view(), name="signup"),
    path("accounts/login/", views.LoginView.as_view(), name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/guide/", views.guide_view, name="guide"),
    path("accounts/signup-list/", views.SignupListView.as_view(), name="signup_list"),
    path("employee/guide/", views.employees_guide_view, name="employees_guide"),
    path("employees/", views.EmployeeListView.as_view(), name="employee_list"),
]
