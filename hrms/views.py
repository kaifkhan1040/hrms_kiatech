
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required(login_url='/user')
def index(request):
    # if request.user.is_authenticated:
    #     return redirect("customadmin:home")
    # if CompanySubscription.objects.filter(id=request.user.id).exists():
    #     return redirect('customadmin:home')
    return render(request,'customadmin/index.html',{'user':request.user})