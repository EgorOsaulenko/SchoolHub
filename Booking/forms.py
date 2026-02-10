from django import forms

from .models import Status, Action, Booking
from Resource.models import Resource


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = "__all__"


class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = "__all__"


class BookingFormUser(forms.ModelForm):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Час початку бронювання")
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}), label="Час завершення бронювання")

    class Meta:
        model = Booking
        exclude = ["user", "created_at", "status", "reason"]


class BookingFormAdmin(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["status", "reason"]