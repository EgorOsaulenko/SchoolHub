import os
import django

# Вказуємо шлях до налаштувань твого проєкту
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolHub.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    username = 'user1111'
    password = 'user111'
    email = 'user111@example.com'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"✅ Суперкористувача '{username}' успішно створено!")
    else:
        print(f"ℹ️ Користувач '{username}' вже існує.")

if __name__ == "__main__":
    create_admin()