from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('users',views.userlist,name='user_list'),
    path('users/create',views.createuser,name='user_create'),
    path('createuser/<int:user_id>/', views.createuser, name='update_user'),
    
    path('leave_type',views.leave_type,name='leave_type'),
    path('leave_type/create',views.createleave_type,name='leave_type_create'),
    path('leave_type_update/<int:leave_id>/',views.createleave_type,name='leave_type_update'),
    path('leave_type_delete/<int:leave_id>/',views.delete_leave_type,name='leave_type_delete'),
    path('leaveresponse/', views.leaveresponse, name='leaveresponse'),
    path('leave',views.leave,name='leave'),
    path('approve_leave/<int:pk>', views.approve_leave, name='approve_leave'),
    path('reject_leave/<int:pk>', views.reject_leave, name='reject_leave'),
    path('attandance/<int:pk>', views.attandance, name='attandance'),

]