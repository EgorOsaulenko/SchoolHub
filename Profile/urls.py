from django.urls import path
from . import views
from django.urls import include


urlpatterns = [
    path("", views.index, name="index"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_in/", views.sign_in, name="sign_in"),
    path("profile/", views.update_profile, name="profile"),
    path("logout/", views.logout_view, name="logout_view"),
    path('accounts/', include('allauth.urls')),
    path('profile/google/login/', views.google_login, name='google_login'),
    path('profile/google/callback/', views.google_callback, name='google_callback'),
]