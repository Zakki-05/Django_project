from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_token, name='generate_token'),
    path('api/activate/', views.activate_token, name='activate_token'),
    path('api/status/', views.queue_status_api, name='queue_status_api'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/login/', views.staff_login_view, name='staff_login'),
    path('staff/logout/', views.staff_logout_view, name='staff_logout'),
    path('staff/book/', views.staff_manual_booking, name='staff_manual_booking'),
    path('staff/action/', views.staff_action, name='staff_action'),
    path('staff-list/', views.staff_list, name='staff_list'),
]
