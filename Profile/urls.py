from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_in/", views.sign_in, name="sign_in"),
    path("profile/", views.update_profile, name="profile"),
    path("logout/", views.logout_view, name="logout_view"),
]