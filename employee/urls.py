from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('checkin', views.check_in, name='checkin'),
    path('checkout', views.check_out, name='checkout'),
    path('leave', views.leave_list, name='leave'),
    path('leave/create', views.apply_leave, name='leave_apply'),

    
    ]