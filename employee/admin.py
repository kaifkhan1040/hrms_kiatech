from django.contrib import admin
from .models import Attendance,CheckIn,CheckOut,LeaveType,LeaveApplication
# Register your models here.
admin.site.register(Attendance)
admin.site.register(CheckIn)
admin.site.register(LeaveType)
admin.site.register(CheckOut)
admin.site.register(LeaveApplication)