from django.db import models
from users.models import CustomUser
from django.utils import timezone
def get_kolkata_time():
    return timezone.localtime(timezone.now())
class CheckIn(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time = models.DateTimeField(default=get_kolkata_time())

    def __str__(self):
        local_time = timezone.localtime(self.time)
        return f"{self.user.email} - {local_time}"

class CheckOut(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time = models.DateTimeField(default=get_kolkata_time())

    def __str__(self):
        return f"{self.user.email} - {self.time}"

class Attendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.ManyToManyField(CheckIn, related_name='attendances')
    check_out = models.ManyToManyField(CheckOut, related_name='attendances')

    def __str__(self):
        return f"{self.user.email} - {self.date}"

    def calculate_working_time(self):
        """
        Calculate the total working hours for a user on this specific day.
        It assumes that check_in and check_out are paired correctly (i.e., 
        there is one check_out for every check_in).
        """
        total_working_time = 0

        # Loop through each pair of check-in and check-out times
        check_ins = self.check_in.all()
        check_outs = self.check_out.all()

        for check_in, check_out in zip(check_ins, check_outs):
            duration = check_out.time - check_in.time
            total_working_time += duration.total_seconds()

        # Convert total seconds to hours
        total_working_time_in_hours = total_working_time / 3600
        return round(total_working_time_in_hours, 2)

class LeaveType(models.Model):
    name = models.CharField(max_length=100, help_text="The type of leave (e.g., Sick Leave, Vacation)")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField(help_text="Start date of the leave")
    end_date = models.DateField(help_text="End date of the leave")
    reason = models.TextField(help_text="Reason for leave")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="approver")
    approval_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.leave_type.name} ({self.status})"

    def days_requested(self):
        return (self.end_date - self.start_date).days + 1