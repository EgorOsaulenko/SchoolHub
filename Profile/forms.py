from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Action, Position, Profile


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="Ім'я")
    last_name = forms.CharField(required=True, label="Прізвище")
    username = forms.CharField(max_length=50, min_length=3, help_text="Введіть свій логін", label="Логін")
    first_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть ім'я", label="Ім'я")
    last_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть прізвище", label="Прізвище")
    email = forms.EmailField(required=False, help_text="Введіть електронну пошту")
    password1 = forms.CharField(help_text="Введіть пароль", label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(help_text="Підтвердіть пароль", label="Підтвердження пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class UserFormEdit(forms.ModelForm):
    username = forms.CharField(max_length=50, min_length=3, help_text="Введіть свій логін", label="Логін")
    first_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть ім'я", label="Ім'я")
    last_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть прізвище", label="Прізвище")
    email = forms.EmailField(required=False, help_text="Введіть електронну пошту")
   

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        fields = ["username", "first_name", "last_name", "email"]

class SignInForm(forms.Form):
    username = forms.CharField(label="Логін")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = "__all__"


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = "__all__"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "phone_number"]
        exclude = ["user", "positions", "balance"]


class SignInForm(forms.Form):
    username = forms.CharField(max_length=50, min_length=3, help_text="Введіть свій логін", label="Логін")
    password = forms.CharField(
        help_text="Введіть пароль",
        label="Пароль",
        widget=forms.PasswordInput,
    )
