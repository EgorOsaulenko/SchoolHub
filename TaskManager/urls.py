from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('computers/', views.pc_list_view, name='computer_list'),
    path('api/status/', views.api_computer_status, name='computer_status_api'),
    path('session/start/<int:computer_id>/', views.computer_start_session, name='start_session'),
    path('booking/start/<int:booking_id>/', views.admin_start_booking_session, name='booking_start'),
    path('session/stop/<int:session_id>/', views.admin_stop_session, name='stop_session'),
    path('booking/cancel/<int:booking_id>/', views.admin_cancel_booking, name='cancel_booking'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('booking/<int:computer_id>/', views.booking_view, name='booking'),
    path('booking/create_book/', views.booking_view, name='booking_create'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('management/computers/', views.staff_pc_management, name='staff_pc_management'),
    path('management/computers/auto-ip/', views.auto_assign_ips, name='auto_assign_ips'),
]
