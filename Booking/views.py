from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import BookingFormAdmin, BookingFormUser
from Profile.models import Position, Action
from .models import Booking, Status, Action as ActionLog, BookingLog
from .permissions import has_permission

# Create your views here.

@has_permission("CB")
@login_required
def create_book(request: HttpRequest):
    form = BookingFormUser(data=request.POST or None)
    if form.is_valid():
        book: Booking = form.save(commit=False)


        if Booking.objects.filter(
            resource=book.resource,
            end_time__gt=book.start_time,
            status=Status.objects.filter(name="Busy").first()
        ).exists():

            messages.error(request, "Даний кабінет ще зайнятий")
            return redirect("resource")
        
        # if book.start_time < datetime.now() or book.end_time <= datetime.now():
        #     messages.error(request, "Дата початку має бути не раніше поточної дати та часу, а завершення - більше поточної дати та часу")
        #     return redirect("resource")

        book.user = request.user
        book.status = Status.objects.filter(name="Waiting").first()
        book.save()

        BookingLog.objects.create(booking=book, user=request.user, action=ActionLog.objects.filter(name="Забронював").first())
        messages.success(request, "Кабінет заброньовано. Очікуйте підтвердження від адміністратора")
        return redirect("resource")
    return render(request, "booking_user.html", dict(form=form))

@has_permission("UB")
@login_required
def update_book(request: HttpRequest, id: int):
    book = Booking.objects.get(pk=id)
    form = BookingFormAdmin(data=request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        name = "Підтвердив" if form.cleaned_data["status"] == Status.objects.filter(name="Busy").first() else "Відхилив"
        BookingLog.objects.create(booking=book, user=request.user, action=ActionLog.objects.filter(name=name).first())
        messages.success(request, "Інформацію оновлено")
        return redirect("resource")
    return render(request, "booking_admin.html", dict(form=form, book=book))

@has_permission("RB")
@login_required
def resources(request: HttpRequest):
    return render(request, "resource.html", dict(booking=Booking.objects.all()))