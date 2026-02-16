from django.urls import path
from django.contrib.auth import views as auth_views
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
    path('booking/start/<int:booking_id>/', views.booking_start, name='booking_start'),
    path('admin/booking/start/<int:computer_id>/', views.admin_start_booking_session, name='admin_start_booking_session'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
