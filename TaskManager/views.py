from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Sum
from decimal import Decimal

from .models import Computer, Session, Tariff, Zone, Booking
from .forms import UserChangeForm, ProfileChangeForm

# Status choices for Matrix UI
STATUS_AVAILABLE = 'FR'
STATUS_BOOKED = 'BK'
STATUS_IN_GAME = 'BS'
STATUS_MAINTENANCE = 'MT'

def is_admin(user):
    return user.is_staff

def get_computer_status_map():
    sessions = Session.objects.filter(is_active=True).select_related('user', 'tariff')
    bookings = Booking.objects.filter(status=STATUS_BOOKED).select_related('computer', 'user')
    session_map = {s.computer_id: s for s in sessions}
    booking_map = {b.computer_id: b for b in bookings}
    return session_map, booking_map

@login_required
def pc_list_view(request: HttpRequest):
    status = request.GET.get('status')
    zone_filter = request.GET.get('zone')
    computers = Computer.objects.all().select_related('zone')
    if status:
        computers = computers.filter(status=status)
    if zone_filter:
        computers = computers.filter(zone__name=zone_filter)
    zones = Zone.objects.all()
    session_map, booking_map = get_computer_status_map()
    for comp in computers:
        comp.active_session = session_map.get(comp.id)
        comp.active_booking = booking_map.get(comp.id)
    context = {
        "computers": [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "zone": c.zone.name if c.zone else "",
                "session": {
                    "user": c.active_session.user.username if c.active_session else None,
                    "tariff": c.active_session.tariff.name if c.active_session and c.active_session.tariff else None,
                    "start_time": c.active_session.start_time.strftime("%H:%M") if c.active_session else None,
                } if c.active_session else None,
                "booking": {
                    "user": c.active_booking.user.username if c.active_booking else None,
                    "start_time": c.active_booking.start_time.strftime("%H:%M %d.%m") if c.active_booking else None,
                    "duration": c.active_booking.duration if c.active_booking else None,
                } if c.active_booking else None,
            }
            for c in computers
        ],
        "zones": [z.name for z in zones],
        "tariffs": list(Tariff.objects.values("id", "name", "price_per_hour")),
        "balance": getattr(request.user.profile, 'balance', 0),
        "is_admin": request.user.is_staff or request.user.is_superuser,
    }
    return render(request, "computer_list.html", context)

@login_required
def profile_view(request: HttpRequest):
    if request.method == 'POST':
        user_form = UserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профіль оновлено.')
            return redirect('profile')
    else:
        user_form = UserChangeForm(instance=request.user)
        profile_form = ProfileChangeForm(instance=request.user.profile)
    return render(request, "profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "balance": getattr(request.user.profile, 'balance', 0),
    })

@login_required
def booking_view(request: HttpRequest, computer_id: int = None):
    computers = Computer.objects.exclude(status=STATUS_MAINTENANCE)
    selected_computer = computers.filter(id=computer_id).first() if computer_id else None
    if request.method == "POST":
        comp_id = request.POST.get("computer")
        start_time = request.POST.get("time")
        duration = request.POST.get("duration")
        computer = get_object_or_404(Computer, id=comp_id)
        Booking.objects.create(
            user=request.user,
            computer=computer,
            start_time=start_time,
            duration=duration,
            status=STATUS_BOOKED
        )
        computer.status = STATUS_BOOKED
        computer.save()
        messages.success(request, "Запит на бронювання надіслано.")
        return redirect("computer_list")
    return render(request, "booking.html", {
        "computers": computers,
        "selected_computer": selected_computer,
        "tariffs": Tariff.objects.all()
    })

@user_passes_test(is_admin)
def admin_start_booking_session(request: HttpRequest, booking_id: int):
    booking = Booking.objects.select_related('computer', 'user').filter(id=booking_id, status=STATUS_BOOKED).first()
    if not booking:
        messages.error(request, "Бронювання не знайдено або не підтверджено.")
        return redirect("computer_list")
    computer = booking.computer
    if computer.status != STATUS_BOOKED:
        messages.error(request, "Комп'ютер не заброньовано.")
        return redirect("computer_list")
    tariff = Tariff.objects.first()
    Session.objects.create(
        user=booking.user,
        computer=computer,
        tariff=tariff,
        start_time=timezone.now(),
        is_active=True
    )
    computer.status = STATUS_IN_GAME
    computer.save()
    booking.status = STATUS_IN_GAME
    booking.save()
    messages.success(request, f"Сесію для {booking.user.username} розпочато.")
    return redirect("computer_list")

@user_passes_test(is_admin)
def computer_start_session(request: HttpRequest, computer_id: int):
    computer = get_object_or_404(Computer, id=computer_id)
    
    if request.method == 'POST':
        username = request.POST.get('user')
        tariff_id = request.POST.get('tariff')
        
        user = User.objects.filter(username=username).first()
        tariff = Tariff.objects.filter(id=tariff_id).first()
        
        if not user or not tariff:
            messages.error(request, "Невірні дані користувача або тарифу.")
            return redirect('computer_start_session', computer_id=computer.id)
            
        if Session.objects.filter(computer=computer, is_active=True).exists():
            messages.error(request, "Комп'ютер вже зайнятий.")
            return redirect('computer_list')

        Session.objects.create(user=user, computer=computer, tariff=tariff, start_time=timezone.now(), is_active=True)
        
        computer.status = STATUS_IN_GAME
        computer.save()
        
        # Automatically close/override any existing booking for this PC
        Booking.objects.filter(computer=computer, status=STATUS_BOOKED).update(status=STATUS_IN_GAME)
        
        messages.success(request, f"Сесію розпочато для {user.username}.")
        return redirect('computer_list')

    return render(request, "session_start.html", {"computer": computer, "tariffs": Tariff.objects.all()})

@user_passes_test(is_admin)
def admin_cancel_booking(request: HttpRequest, booking_id: int):
    booking = Booking.objects.filter(id=booking_id, status=STATUS_BOOKED).first()
    if not booking:
        messages.error(request, "Бронювання не знайдено.")
        return redirect("computer_list")
    booking.status = 'cancelled'
    booking.save()
    booking.computer.status = STATUS_AVAILABLE
    booking.computer.save()
    messages.success(request, "Бронювання скасовано.")
    return redirect("computer_list")

@user_passes_test(is_admin)
def admin_stop_session(request: HttpRequest, session_id: int):
    session = Session.objects.filter(id=session_id, is_active=True).select_related('computer', 'user').first()
    if not session:
        messages.error(request, "Активну сесію не знайдено.")
        return redirect("computer_list")
    end_time = timezone.now()
    duration = (end_time - session.start_time).total_seconds() / 3600
    cost = Decimal(duration) * session.tariff.price_per_hour
    session.end_time = end_time
    session.total_cost = cost
    session.is_active = False
    session.save()
    computer = session.computer
    computer.status = STATUS_AVAILABLE
    computer.save()
    profile = session.user.profile
    profile.balance -= cost
    profile.save()
    messages.success(request, f"Сесію завершено. До сплати: {cost:.2f} грн")
    return redirect("computer_list")

@login_required
def statistics_view(request: HttpRequest):
    sessions = Session.objects.filter(user=request.user, is_active=False)
    total_spent = sessions.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    total_seconds = sum(
        (s.end_time - s.start_time).total_seconds()
        for s in sessions if s.start_time and s.end_time
    )
    total_hours = round(total_seconds / 3600, 2)
    return render(request, "statistics.html", {
        "total_hours": total_hours,
        "total_spent": total_spent
    })

@login_required
def api_computer_status(request: HttpRequest):
    computers = Computer.objects.all()
    session_map, booking_map = get_computer_status_map()
    data = [
        {
            "id": c.id,
            "status": c.status,
            "session": {
                "user": session_map[c.id].user.username,
                "tariff": session_map[c.id].tariff.name,
                "start_time": session_map[c.id].start_time.strftime("%H:%M"),
            } if c.id in session_map else None,
            "booking": {
                "user": booking_map[c.id].user.username,
                "start_time": booking_map[c.id].start_time.strftime("%H:%M %d.%m"),
                "duration": booking_map[c.id].duration,
            } if c.id in booking_map else None,
        }
        for c in computers
    ]
    return JsonResponse({"computers": data})

@user_passes_test(is_admin)
def staff_pc_management(request: HttpRequest):
    if request.method == "POST":
        computer_id = request.POST.get("computer_id")
        new_status = request.POST.get("status", "")
        
        computer = get_object_or_404(Computer, id=computer_id)
        
        # Перевіряємо, чи є такий статус у списку доступних
        valid_statuses = [choice[0] for choice in Computer.StatusChoice.choices]
        if new_status in valid_statuses:
            computer.status = new_status
            computer.save()
            messages.success(request, f"Статус комп'ютера {computer.name} змінено.")
        else:
            messages.error(request, "Помилка: обрано некоректний статус.")
        
        return redirect("staff_pc_management")

    computers = Computer.objects.all().order_by('zone', 'name')
    return render(request, "admin_pc_management.html", {
        "computers": computers,
        "status_choices": Computer.StatusChoice.choices
    })

@user_passes_test(is_admin)
def auto_assign_ips(request: HttpRequest):
    # Сортуємо, щоб IP видавалися логічно (по зонах, потім по назві)
    computers = Computer.objects.all().order_by('zone', 'name')
    start_octet = 101
    
    for computer in computers:
        computer.ip_address = f"128.0.0.{start_octet}"
        computer.save()
        start_octet += 1
        
    messages.success(request, "IP-адреси успішно призначено (починаючи з 128.0.0.).")
    return redirect("staff_pc_management")
