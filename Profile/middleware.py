from django.contrib.auth.models import User
from django.http import HttpRequest


class PrefetchUser:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.user.is_authenticated:
            request.user = User.objects.prefetch_related("profile__positions__actions").get(pk=request.user.pk)
            
        response = self.get_response(request)
        return response