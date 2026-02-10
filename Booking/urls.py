from django.urls import path

from . import views


urlpatterns = [
    path("create_book/", views.create_book, name="create_book"),
    path("update_book/<int:id>/", views.update_book, name="update_book"),
    path("", views.resources, name="resource"),
]