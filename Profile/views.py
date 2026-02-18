import locale
from datetime import datetime
import requests
from django.conf import settings
from django.utils.crypto import get_random_string

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.db.models import Q

from .models import Profile, Position, Action
from .forms import UserForm, UserFormEdit, SignInForm, ActionForm, ProfileForm, PositionForm

# Create your views here.


def sign_up(request: HttpRequest):
    if request.method == "POST":
        sign_up_form = UserForm(request.POST)
        profile_form = ProfileForm(data=request.POST, files=request.FILES)
        if sign_up_form.is_valid():
            user = sign_up_form.save()
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            else:
                profile = Profile(user=user)
                profile.save()

            messages.success(request, "Вітаємо з реєстрацією!")
            return redirect("sign_in")

        messages.error(request, sign_up_form.errors)
        return redirect("sign_up")
    return render(request, "sign_up.html", dict(sign_up_form=UserForm(), profile_form=ProfileForm()))



def sign_in(request: HttpRequest):
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password")
            )
            if user:
                login(request, user)
                messages.success(request, "Вітаємо з поверненням!")
                return redirect("index")
            else:
                messages.error(request, "Користувача з такими параметрами не знайдено")
                return redirect("sign_in")
            
        messages.error(request, form.errors)
        return redirect("sign_in")
    
    return render(request, "sign_in.html", dict(form=SignInForm()))


@login_required
def update_profile(request: HttpRequest):
    if request.method == "POST":
        user_form = UserFormEdit(data=request.POST, instance=request.user)
        profile_form = ProfileForm(data=request.POST, files=request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Дані успішно оновлено")
            return redirect("profile")
        if profile_form.errors:
            messages.error(request, "Помилка: перевірте аватар (формат, розмір)")
    else:
        user_form = UserFormEdit(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, "profile.html", dict(user_form=user_form, profile_form=profile_form))


@login_required
def index(request: HttpRequest):
    return render(request, "index.html")



@login_required
def logout_view(request: HttpRequest):
    logout(request)
    messages.success(request, "Ви успішно вийшли з системи. До зустрічі!")
    return redirect("sign_in")

def google_login(request: HttpRequest):
    """Ініціює вхід через Google (OAuth 2.0)."""
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    redirect_uri = getattr(settings, "GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/profile/google/callback/")
    scope = "email profile"
    
    # Генеруємо випадковий стан для захисту від CSRF
    state = get_random_string(32)
    request.session["google_oauth_state"] = state
    
    # Формуємо URL для перенаправлення користувача на Google
    url = f"{base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}&access_type=offline"
    return redirect(url)

def google_callback(request: HttpRequest):
    """Обробляє повернення користувача від Google."""
    code = request.GET.get("code")
    state = request.GET.get("state")
    stored_state = request.session.get("google_oauth_state")

    # Перевірка безпеки
    if not code or not state or state != stored_state:
        messages.error(request, "Помилка авторизації Google (невірний стан).")
        return redirect("sign_in")

    # Обмін коду на токен доступу
    token_url = "https://oauth2.googleapis.com/token"
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
    redirect_uri = getattr(settings, "GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/profile/google/callback/")

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    res = requests.post(token_url, data=data)
    if not res.ok:
        messages.error(request, "Не вдалося отримати токен доступу від Google.")
        return redirect("sign_in")
    
    # Отримання даних користувача
    access_token = res.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", params={"access_token": access_token}).json()
    
    email = user_info.get("email")
    if email:
        # Шукаємо користувача за email або створюємо нового
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(username=email.split("@")[0], email=email)
            Profile.objects.create(user=user)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, f"Вітаємо, {user.username}!")
        return redirect("index")
    
    messages.error(request, "Google не надав email.")
    return redirect("sign_in")