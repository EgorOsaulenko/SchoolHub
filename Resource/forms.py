from django import forms

from .models import Resource, Location


class ResourceForm(forms.ModelForm):
    location = forms.ModelChoiceField(
        queryset=Location.objects.all()
    )
    
    class Meta:
        model = Resource
        fields = "__all__"


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = "__all__"