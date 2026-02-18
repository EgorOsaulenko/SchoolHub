from django import forms

from .models import Status, Booking


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = "__all__"


class BookingFormUser(forms.ModelForm):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        "type": "datetime-local",
        "class": "w-full bg-[#2d2d2d] text-white border border-gray-600 rounded p-2 focus:border-[#ff6600] focus:ring-1 focus:ring-[#ff6600] outline-none",
        "style": "color-scheme: dark;"
    }), label="Час початку бронювання")
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        "type": "datetime-local",
        "class": "w-full bg-[#2d2d2d] text-white border border-gray-600 rounded p-2 focus:border-[#ff6600] focus:ring-1 focus:ring-[#ff6600] outline-none",
        "style": "color-scheme: dark;"
    }), label="Час завершення бронювання")

    class Meta:
        model = Booking
        exclude = ["user", "created_at", "status", "reason"]


class BookingFormAdmin(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["status", "reason"]