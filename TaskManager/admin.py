from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html

from .models import Zone, Tariff, Computer, Session, Payment, Booking


class BookingAdmin(admin.ModelAdmin):
	list_display = ('user', 'computer', 'start_time', 'duration', 'status', 'start_button')

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('<int:booking_id>/start-session/', self.admin_site.admin_view(self.start_session_view), name='taskmanager_booking_start_session'),
		]
		return custom_urls + urls

	def start_button(self, obj):
		# Show button only when booking is not rejected and computer appears booked
		url = reverse('admin:taskmanager_booking_start_session', args=[obj.pk])
		return format_html(
			'<a class="button" href="{}">Старт</a>',
			url
		)
	start_button.short_description = 'Дія'
	start_button.allow_tags = True

	def start_session_view(self, request, booking_id, *args, **kwargs):
		booking = get_object_or_404(Booking, pk=booking_id)
		# Prevent starting if computer already busy
		computer = booking.computer
		if computer.status == Computer.StatusChoice.BUSY:
			messages.error(request, 'Компьютер вже зайнятий.')
			return redirect(request.META.get('HTTP_REFERER', reverse('admin:taskmanager_booking_changelist')))

		# Create a session for the booking's user and computer
		session = Session.objects.create(user=booking.user, computer=computer, tariff=None)
		computer.status = Computer.StatusChoice.BUSY
		computer.save()
		# Mark booking as approved (started)
		booking.status = 'approved'
		booking.save()

		messages.success(request, f'Сесія запущена для {booking.user.username} на {computer.name}.')
		return redirect(request.META.get('HTTP_REFERER', reverse('admin:taskmanager_booking_changelist')))


admin.site.register(Booking, BookingAdmin)
admin.site.register([Zone, Tariff, Computer, Session, Payment])