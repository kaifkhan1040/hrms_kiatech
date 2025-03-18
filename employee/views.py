from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import CustomUser
from django.utils import timezone
from .models import Attendance, CheckIn, CheckOut,LeaveApplication
from .forms import LeaveApplicationForm
from datetime import datetime
import calendar
from datetime import timedelta
from users.email import apply_user_leave
# Create your views here.

def attendance_report(user,search_year,search_month):
    current_date = datetime.now()
    year = int(search_year)
    month = int(search_month)
    obj={}
    _, num_days = calendar.monthrange(year, month)
    if year==current_date.year and month==current_date.month:
        num_days=current_date.day
    sundays=[]
    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()
        if date.weekday() == 6:
            sundays.append(date)
    attendance_records = Attendance.objects.filter(
    user=user, 
    date__year=current_date.year,  
    date__month=current_date.month 
    ).values('date')
    attendance_records=[i['date'] for i in attendance_records]
    print('attendance',attendance_records)

    approved_leaves = LeaveApplication.objects.filter(
    user=user, 
    status='Approved',
    )
    all_leave_days = []

    for leave in approved_leaves:
        current_date = leave.start_date
        while current_date <= leave.end_date:
            if month!=current_date.month:
                break
            all_leave_days.append(current_date)
            current_date += timedelta(days=1)
    obj_list=[]
    for day in range(num_days, 0, -1):
        date = datetime(year, month, day).date()
        obj['date']=date
        if date in sundays:
            obj['attendance']='Week off'
        elif date in all_leave_days:
            obj['attendance']='Leave'
        elif date in attendance_records:
            print('run')
            today_attendance = Attendance.objects.filter(user=user, date=date).first()
            print('run2',today_attendance)
            obj['total_working_time'] = today_attendance.calculate_working_time()
            obj['attendance']='Present'
            obj['check_in_time'] = timezone.localtime(today_attendance.check_in.first().time).time()
            obj['check_out_time'] = timezone.localtime(today_attendance.check_out.last().time).time() if today_attendance.check_out.exists() else 0.0
        else:
            obj['attendance']='Absent'
        obj_list.append(obj)
        obj={}
    return obj_list
        
    


@login_required(login_url='/user')
def home(request):
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
    attendance_full_report=attendance_report(request.user,current_year,current_month)
    check_in_exists=False
    show_button=False
    check_out_exists=False
    check_in_time=None
    today_attendance = Attendance.objects.filter(user=request.user, date=timezone.localtime(timezone.now()).date()).first()
    if today_attendance:
        total_working_time = today_attendance.calculate_working_time()
        check_in_exists = today_attendance.check_in.exists()
        check_in_time = today_attendance.check_in.first().time.time()
        check_out_exists = today_attendance.check_out.exists()
        if today_attendance.check_in.all().count()>today_attendance.check_out.all().count():
            show_button=True
    else:
        total_working_time = 0
    return render(request,'employe/index.html',{'user':request.user,
                    'total_working_time': total_working_time, 'check_in_exists': check_in_exists,
            'check_out_exists': check_out_exists,'show_button':show_button,'check_in_time':check_in_time,
            'attendance_report':attendance_full_report,'years': years, 
        'months': months, 'current_year': current_year,'current_month': current_month,'month_name':month_name
                    })


@login_required
def check_in(request):
    today_attendance = Attendance.objects.filter(user=request.user, date=timezone.localtime(timezone.now()).date()).first()

    if today_attendance:
        check_in_time = CheckIn.objects.create(user=request.user, time=timezone.localtime(timezone.now()))
        today_attendance.check_in.add(check_in_time)
        messages.success(request, "Checked in successfully.")
    else:
        attendance = Attendance.objects.create(user=request.user, date=timezone.localtime(timezone.now()).date())
        check_in_time = CheckIn.objects.create(user=request.user, time=timezone.localtime(timezone.now()))
        attendance.check_in.add(check_in_time)  # Add the CheckIn to the attendance
        messages.success(request, "Checked in successfully.")

    return redirect('employe:home')

@login_required
def check_out(request):
    today_attendance = Attendance.objects.filter(user=request.user, date=timezone.localtime(timezone.now()).date()).first()

    if today_attendance:
        check_out_time = CheckOut.objects.create(user=request.user, time=timezone.localtime(timezone.now()))
        today_attendance.check_out.add(check_out_time)
        messages.success(request, "Checked out successfully.")
    else:
        messages.error(request, "No attendance record found for today.")

    return redirect('employe:home')

@login_required(login_url='/user')
def leave_list(request):
    data=LeaveApplication.objects.filter(user=request.user)[::-1]
    return render(request,'employe/leave.html',{'user':request.user,'data':data})


@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave_application = form.save(commit=False)
            leave_application.user = request.user 
            leave_application.save()
            print('leave app',leave_application,"id",leave_application.id)
            superuser=CustomUser.objects.filter(is_superuser=True).first()
            print('super user',superuser)
            apply_user_leave(leave_application,superuser)
            messages.success(request, "Leave Applyed Successfully")
            return redirect('employe:leave')
    else:
        form = LeaveApplicationForm()
    
    return render(request, 'employe/apply_leave.html', {'form': form})

