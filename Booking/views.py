from datetime import datetime

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import BookingFormAdmin, BookingFormUser
from Profile.models import Position, Action
from .models import Booking, Status, BookingLog
from .permissions import has_permission
from TaskManager.models import Computer

# Create your views here.

@has_permission("CB")
@login_required
def create_book(request: HttpRequest):
    form = BookingFormUser(data=request.POST or None)
    if form.is_valid():
        book: Booking = form.save(commit=False)


        if Booking.objects.filter(
            computer=book.computer,
            end_time__gt=book.start_time,
            status=Status.objects.filter(name="Busy").first()
        ).exists():

            messages.error(request, "Даний комп'ютер вже заброньовано на цей час")
            return redirect("computer_list")
        
        # if book.start_time < datetime.now() or book.end_time <= datetime.now():
        #     messages.error(request, "Дата початку має бути не раніше поточної дати та часу, а завершення - більше поточної дати та часу")
        #     return redirect("resource")

        book.user = request.user
        book.status = Status.objects.filter(name="Waiting").first()
        book.save()
        
        BookingLog.objects.create(booking=book, user=request.user, action="Створив бронювання")
        messages.success(request, "Комп'ютер заброньовано. Очікуйте підтвердження від адміністратора")
        return redirect("computer_list")
    return render(request, "booking_user.html", dict(form=form))

@has_permission("MB")
@login_required
def update_book(request: HttpRequest, id: int):
    book = Booking.objects.get(pk=id)
    form = BookingFormAdmin(data=request.POST or None, instance=book)
    if form.is_valid():
        saved_book = form.save()
        
        if saved_book.status and (saved_book.status.name == "Busy" or saved_book.status.name == "Confirmed"):
            if saved_book.computer:
                saved_book.computer.status = Computer.StatusChoice.BOOKED
                saved_book.computer.save()
            name = "Підтвердив"
        else:
            name = "Відхилив"

        BookingLog.objects.create(booking=saved_book, user=request.user, action=name)
        messages.success(request, "Інформацію оновлено")
        return redirect("resource")
    return render(request, "booking_admin.html", dict(form=form, book=book))

@has_permission("MB")
@login_required
def resources(request: HttpRequest):
    # Автоматичне скасування прострочених заявок
    waiting_status = Status.objects.filter(name="Waiting").first()
    rejected_status = Status.objects.filter(name="Rejected").first()
    
    if waiting_status and rejected_status:
        # Знаходимо заявки, час початку яких вже минув, а статус все ще "Waiting"
        expired_bookings = Booking.objects.filter(status=waiting_status, start_time__lt=timezone.now())
        for book in expired_bookings:
            book.status = rejected_status
            book.save()
            BookingLog.objects.create(booking=book, user=request.user, action="Автоматично відхилено (прострочено)")

    bookings = Booking.objects.select_related('computer', 'status', 'user').all().order_by('-id')
    if not request.user.is_staff:
        bookings = bookings.filter(user=request.user)
    return render(request, "resource.html", dict(booking=bookings))