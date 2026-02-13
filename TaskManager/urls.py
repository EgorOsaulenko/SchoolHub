from django.urls import path
from . import views

urlpatterns = [
    path('computers/', views.computer_list_view, name='computer_list'),
    path('api/status/', views.computer_status_api, name='computer_status_api'),
    path('session/start/<int:computer_id>/', views.start_session, name='start_session'),
    path('session/stop/<int:session_id>/', views.stop_session, name='stop_session'),
    path('statistics/', views.statistics_view, name='statistics'),
    
    path('booking/<int:computer_id>/', views.booking_view, name='booking'),
    path('booking/list/', views.booking_list_view, name='booking_list'),
    path('booking/manage/<int:booking_id>/<str:action>/', views.booking_manage, name='booking_manage'),
]
