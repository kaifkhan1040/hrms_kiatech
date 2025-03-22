from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import CustomUser
from django.http import JsonResponse
from users.forms import CustomUserCreationForm,UserProfileForm
from employee.models import LeaveType,LeaveApplication,Attendance
from employee.forms import LeaveTypeForm,LeaveApplicationForm
from django.utils import timezone
from employee.views import attendance_report
from datetime import datetime
import calendar
from django.db import connection
from datetime import timedelta
from django.http import HttpResponse
from django.core.management import call_command
import os
from django.conf import settings
from users.email import leave_aproved_mail,leave_reject_mail

# Create your views here.
@login_required(login_url='/user')
def home(request):
    print('run')
    all_user=CustomUser.objects.all().count()
    inactive_user=CustomUser.objects.filter(is_active=False).count()
    active_user=CustomUser.objects.filter(is_active=True).count()
    user_list=CustomUser.objects.filter(is_active=True,is_superuser=False)
    today = datetime.today().date()
    working_user=[]
    for i in user_list:
        temp_dict={}
        temp_dict['username']=i.first_name+' '+i.last_name
        approved_leaves = LeaveApplication.objects.filter(
        user=i, 
        status='Approved',
        )
        all_leave_days = []

        for leave in approved_leaves:
            current_date = leave.start_date
            while current_date <= leave.end_date:
                # if month!=current_date.month:
                #     break
                all_leave_days.append(current_date)
                current_date += timedelta(days=1)
        print('leave:',all_leave_days,'today',today)
        if today.weekday() == 6:
            temp_dict['attendance']='Week off'
        elif today in all_leave_days:
            temp_dict['attendance']='Leave'
        else:
            today_attendance = Attendance.objects.filter(user=i, date=timezone.localtime(timezone.now()).date()).first()
            if today_attendance:
                temp_dict['total_working_time'] = today_attendance.calculate_working_time()
                temp_dict['check_in_time'] =  timezone.localtime(today_attendance.check_in.first().time).time()
                temp_dict['check_out_time'] = timezone.localtime(today_attendance.check_out.last().time).time() if today_attendance.check_out.exists() else None
                temp_dict['attendance']='Present'
            else:
                temp_dict['attendance']='absent'
        working_user.append(temp_dict)
    print('^'*100,working_user)
    return render(request,'customadmin/index.html',{'user':request.user,
                    'all_user':all_user,'inactive_user':inactive_user,
                    'active_user':active_user,'working_user':working_user})

def userlist(request):
    obj=request.GET.get('search')
    data = CustomUser.objects.filter(is_superuser=False).order_by('-id')
    if obj in ['1','0']:
        data = CustomUser.objects.filter(is_active=obj,is_superuser=False).order_by('-id')
    all_user=CustomUser.objects.all().count()
    inactive_user=CustomUser.objects.filter(is_active=False).count()
    active_user=CustomUser.objects.filter(is_active=True).count()
    return render(request,'customadmin/userlist.html',{
        'all_user':all_user,'inactive_user':inactive_user,'active_user':active_user,
        'data':data
    })

def createuser(request,user_id=None):
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id)
        form = UserProfileForm(instance=user)
    else:
        user = None
        form = CustomUserCreationForm()
    if request.method=="POST":
        if user_id:
            user = get_object_or_404(CustomUser, id=user_id)
            form = UserProfileForm(request.POST,request.FILES,instance=user)
        else:
            form=CustomUserCreationForm(request.POST,request.FILES,instance=user)
        email=request.POST.get('email')
        designation=request.POST.get('designation')
        salary=request.POST.get('salary')
        if form.is_valid():
            status=request.POST.get('status')
            print('sssssssssssssssssss',status)
            updated_user = form.save()
            updated_user.is_active=True if status=='1' else False
            updated_user.designation=designation
            updated_user.salary=salary
            updated_user.save()
            action = 'updated' if user else 'created'
            messages.success(request, f'User {updated_user.email} has been {action} successfully!')
            return redirect('customadmin:user_list')
        else:
            print('errrrrrrrr',form.errors)
            messages.error(request,form.errors)
    return render(request,'customadmin/createuser.html',{'form':form,'user1':user
        })

def leave_type(request):
    data=LeaveType.objects.all().order_by('-id')
    return render(request,'customadmin/leave_type.html',{
        'data':data
    })

def createleave_type(request,leave_id=None):
    if leave_id:
        leave_type = get_object_or_404(LeaveType, id=leave_id)
        form = LeaveTypeForm(instance=leave_type)
    else:
        leave_type = None
        form = LeaveTypeForm()
    if request.method=="POST":
        if leave_id:
            leave_type = get_object_or_404(LeaveType, id=leave_id)
            form = LeaveTypeForm(request.POST,instance=leave_type)
        else:
            form=LeaveTypeForm(request.POST,instance=leave_type)
        if form.is_valid():
            updated_user = form.save()
            action = 'updated' if leave_type else 'created'
            messages.success(request, f'Leave Type {updated_user.name} has been {action} successfully!')
            return redirect('customadmin:leave_type')
        else:
            print('errrrrrrrr',form.errors)
            messages.error(request,form.errors)
    return render(request,'customadmin/create_leave_type.html',{'form':form,'leave_type':leave_type
        })

def delete_leave_type(request,leave_id):
    leave_type = get_object_or_404(LeaveType, id=leave_id)
    leave_type.delete()
    messages.success(request, f'Leave Type has been deleted successfully!')
    return redirect('customadmin:leave_type')

def leave(request):
    data=LeaveApplication.objects.all().order_by('-id')
    obj=request.GET.get('search')
    if obj in ['Pending','Approved','Rejected']:
        data=LeaveApplication.objects.filter(status=obj).order_by('-id')
    return render(request,'customadmin/leave.html',{
        'data':data
    })

@login_required(login_url='/user')
def approve_leave(request,pk):
    obj=LeaveApplication.objects.get(id=pk)
    obj.status='Approved'
    obj.save()
    leave_aproved_mail(
        obj.user.first_name+obj.user.last_name if obj.user.last_name else "",
        obj.user.email,obj)
    return JsonResponse(True,safe=False)

@login_required(login_url='/user')
def reject_leave(request,pk):
    obj=LeaveApplication.objects.get(id=pk)
    obj.status='Rejected'
    obj.save()
    leave_reject_mail(
        obj.user.first_name+obj.user.last_name if obj.user.last_name else "",
        obj.user.email,obj)
    return JsonResponse(True,safe=False)

def leaveresponse(request):
    backup_file_path = os.path.join(settings.BASE_DIR, 'backup', 'database_backup.sql')
    os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
    call_command('dbbackup', '--output-filename', backup_file_path)
    with open(backup_file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/sql')
        response['Content-Disposition'] = 'attachment; filename="database_backup.sql"'
    os.remove(backup_file_path)
    return response

def leavedel(request):
    try:
        call_command('flush', '--no-input')
        return HttpResponse(" successfully!", content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"Error flushing: {str(e)}", content_type="text/plain")

@login_required(login_url='/user')
def attandance(request,pk):
    user=CustomUser.objects.filter(id=pk).first()
    current_year = timezone.now().year
    current_month = timezone.now().month
    now = timezone.localtime(timezone.now())
    # search_year=current_year
    # search_month=current_month
    years = tuple(range(2020, current_year + 1))

    months = [
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]
    select_year=request.GET.get('select_year')
    select_month=request.GET.get('select_month')
    
    if select_year:
        current_year=select_year
    if select_month:
        current_month=select_month
    month_name=datetime(int(current_year), int(current_month), 1).date()
    print('name',month_name,type(month_name))
    attendance_full_report=attendance_report(user,current_year,current_month)
    return render(request,'customadmin/attandance.html',{'user':user,
         'attendance_report':attendance_full_report,'years': years, 
        'months': months, 'current_year': current_year,'current_month': current_month,'month_name':month_name
    })
