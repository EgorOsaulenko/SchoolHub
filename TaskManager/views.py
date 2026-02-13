from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from .models import Computer, Session, Tariff, Payment, Zone, Booking
# from .forms import SessionForm # Припускаємо, що форму ви оновите окремо
from Booking.permissions import has_permission

# Create your views here.


@require_GET
def computer_list_view(request: HttpRequest):
    computers = Computer.objects.all().select_related('zone')
    zones = Zone.objects.all()
    
    # Отримуємо активні сесії для відображення на картках
    active_sessions = Session.objects.filter(is_active=True).select_related('user', 'tariff')
    sessions_map = {s.computer_id: s for s in active_sessions}

    for comp in computers:
        comp.active_session = sessions_map.get(comp.id)
        
    context = {"computers": computers, "zones": zones}
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            context['balance'] = request.user.profile.balance
        # Flag to hide admin panel for non-staff users
        context['is_staff'] = request.user.is_staff

    return render(request, "computer_list.html", context)


def computer_status_api(request: HttpRequest):
    computers = Computer.objects.all()
    active_sessions = Session.objects.filter(is_active=True).select_related('user', 'tariff')
    sessions_map = {s.computer_id: s for s in active_sessions}
    
    data = []
    for comp in computers:
        session = sessions_map.get(comp.id)
        session_info = None
        if session:
            session_info = {
                "user": session.user.username,
                "tariff": session.tariff.name if session.tariff else "-",
                "start_time": session.start_time.strftime("%H:%M"),
                "id": session.id
            }
            
        data.append({
            "id": comp.id,
            "status": comp.status,
            "status_display": comp.get_status_display(),
            "session": session_info
        })
        
    return JsonResponse({"computers": data})

@has_permission("MS") # Manage Sessions
def start_session(request: HttpRequest, computer_id: int):
    if not request.user.is_staff:
        messages.error(request, "Тільки адміністратори можуть відкривати сесії.")
        return redirect("computer_list")

    computer = Computer.objects.get(id=computer_id)
    
    if request.method == "POST":
        tariff_id = request.POST.get("tariff")
        username = request.POST.get("user")
        
        tariff = Tariff.objects.get(id=tariff_id)
        
        # Перевірка статусу ПК
        if computer.status != Computer.StatusChoice.FREE and computer.status != Computer.StatusChoice.BOOKED:
            messages.error(request, "Цей комп'ютер зараз зайнятий або на обслуговуванні.")
            return redirect("computer_list")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f"Користувача '{username}' не знайдено.")
            return redirect("computer_list")

        # Створення сесії
        Session.objects.create(
            user=user,
            computer=computer,
            tariff=tariff
        )
        
        # Оновлення статусу ПК
        computer.status = Computer.StatusChoice.BUSY
        computer.save()
        
        messages.success(request, f"Сесію на {computer.name} розпочато.")
        return redirect("computer_list")
    
    tariffs = Tariff.objects.all()
    return render(request, "session_start.html", {"computer": computer, "tariffs": tariffs})


@has_permission("MS")
def stop_session(request: HttpRequest, session_id: int):
    if not request.user.is_staff:
        messages.error(request, "Тільки адміністратори можуть завершувати сесії.")
        return redirect("computer_list")

    session = Session.objects.filter(id=session_id, is_active=True).first()
    if not session:
        messages.error(request, "Активну сесію не знайдено")
        return redirect("computer_list")
    
    # Розрахунок часу та вартості
    end_time = timezone.now()
    duration = (end_time - session.start_time).total_seconds() / 3600 # Години
    cost = Decimal(duration) * session.tariff.price_per_hour
    
    # Оновлення сесії
    session.end_time = end_time
    session.total_cost = cost
    session.is_active = False
    session.save()

    # Звільнення ПК
    computer = session.computer
    computer.status = Computer.StatusChoice.FREE
    computer.save()

    # Списання грошей (приклад)
    profile = session.user.profile
    profile.balance -= cost
    profile.save()

    messages.success(request, f"Сесію завершено. До сплати: {cost:.2f} грн")
    return redirect("computer_list")


@login_required
def statistics_view(request: HttpRequest):
    # VS (Перегляд статистики): Тільки особиста статистика гравця
    sessions = Session.objects.filter(user=request.user, is_active=False)
    
    total_spent = sessions.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    total_seconds = 0
    for s in sessions:
        if s.start_time and s.end_time:
            total_seconds += (s.end_time - s.start_time).total_seconds()
            
    total_hours = round(total_seconds / 3600, 2)
    
    return render(request, "statistics.html", {"total_hours": total_hours, "total_spent": total_spent})

@login_required
def booking_view(request: HttpRequest, computer_id: int = None):
    computers = Computer.objects.all()
    selected_computer = None
    if computer_id:
        selected_computer = Computer.objects.filter(id=computer_id).first()
    
    if request.method == "POST":
        comp_id = request.POST.get("computer")
        start_time = request.POST.get("time")
        duration = request.POST.get("duration")
        
        Booking.objects.create(
            user=request.user,
            computer_id=comp_id,
            start_time=start_time,
            duration=duration
        )
        messages.success(request, "Запит на бронювання надіслано. Очікуйте підтвердження.")
        return redirect("computer_list")
        
    return render(request, "booking.html", {
        "computers": computers,
        "selected_computer": selected_computer,
        "tariffs": Tariff.objects.all()
    })

@login_required
def booking_list_view(request: HttpRequest):
    if not request.user.is_staff:
        messages.error(request, "Доступ заборонено")
        return redirect("computer_list")
        
    bookings = Booking.objects.filter(status='pending').order_by('start_time')
    return render(request, "booking_list.html", {"bookings": bookings})

@login_required
def booking_manage(request: HttpRequest, booking_id: int, action: str):
    if not request.user.is_staff:
        return redirect("computer_list")
        
    booking = Booking.objects.get(id=booking_id)
    
    if action == 'approve':
        booking.status = 'approved'
        booking.save()
        booking.computer.status = Computer.StatusChoice.BOOKED
        booking.computer.save()
        messages.success(request, f"Бронювання для {booking.user} підтверджено.")
    elif action == 'reject':
        booking.status = 'rejected'
        booking.save()
        messages.success(request, "Бронювання відхилено.")
        
    return redirect("booking_list")
