from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile, Action, Position, Subject


class UserForm(UserCreationForm):
    username = forms.CharField(max_length=50, min_length=3, help_text="Введіть свій логін", label="Логін")
    first_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть ім'я", label="Ім'я")
    last_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть прізвище", label="Прізвище")
    email = forms.EmailField(required=False, help_text="Введіть електронну пошту")
    password1 = forms.CharField(help_text="Введіть пароль", label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(help_text="Підтвердіть пароль", label="Підтвердження пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class UserFormEdit(forms.ModelForm):
    username = forms.CharField(max_length=50, min_length=3, help_text="Введіть свій логін", label="Логін")
    first_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть ім'я", label="Ім'я")
    last_name = forms.CharField(max_length=50, min_length=3, help_text="Введіть прізвище", label="Прізвище")
    email = forms.EmailField(required=False, help_text="Введіть електронну пошту")
   

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]



class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = "__all__"


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = "__all__"


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = "__all__"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user", "positions", "class_room"]


class SignInForm(forms.Form):
    username = forms.CharField(max_length=50, min_length=3, help_text="Введіть свій логін", label="Логін")
    password = forms.CharField(
        help_text="Введіть пароль",
        label="Пароль",
        widget=forms.PasswordInput,
    )