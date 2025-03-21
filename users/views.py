from http import cookies
from http.client import responses
from django.views import generic
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ResetPasswordForm
from django.core.mail import send_mail
from .models import ForgetPassMailVerify#, FpoEmailVerify
from .models import CustomUser,UserEmailVerify,UserNumberVerify
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
import urllib.request
import urllib.parse
from .email import verification_mail

def sendSMS(apikey, numbers, sender, message):
    data = urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
                                   'message': message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return (fr)


from time import strftime
def compnay_id(compnay,comp_len):
    com=compnay[0:2]
    time_yy = strftime('%Y')[2:4]
    time_mm= strftime('%m')
    val=4-len(str(len(comp_len)+1))
    zero='0'*val
    id_of_comp=str(com)+str(time_mm)+str(time_yy)+str(zero)+str(len(comp_len)+1)
    return id_of_comp
##compnay name+mm+yy+0001

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('user:login'))
    

def signup(request):
    form=CustomUserCreationForm()
    if request.method=="POST":
        form=CustomUserCreationForm(request.POST)
        email=request.POST.get('email')
        if form.is_valid():
            signup_as = form.cleaned_data['role']
            preobj=form.save(commit=False)
            preobj.is_active=False
            preobj.save()
            email1 = CustomUser.objects.get(email=email)
            UserNumberVerify.objects.create(user=preobj)
            messages.success(request,'Please Verify your email.')
            token = get_random_string(16)
            UserEmailVerify(user=email1, link=token).save()
            token = 'http://'+str(get_current_site(request).domain)+'/user/userverify/' + token
            verification_mail(token, email)
            msg = 'The activation link has been send to your Email.'
            return redirect('user:login')
        else:
            messages.error(request,form.errors)
    return render(request,'registration/signup.html',{'form':form})

# def login(request):
#     if request.method == 'POST':
#         email = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=email, password=password)
#         if email is not None:
#             form = login(request)
#             messages.success(request, f' welcome {email} !!')
#             return redirect('index')
#         else:
#             messages.info(request, f'account done not exit plz sign in')
#     form = AuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form, 'title': 'log in'})
# from landload.models import EmailTemplate
from django.template import Template, Context
def checkemail(request):
    pass
    # email_template = "email/customemail.html"
    # objectdata=EmailTemplate.objects.get(id=2)
    # context_data = {'data': 'kaifkhan'}
    # objectdata_rendered = Template(objectdata.body).render(Context(context_data))
    # return render(request,'email/customemail.html',{'object':objectdata,"data":"kaif","objectdata_rendered":objectdata_rendered})
# Create your views here.
def loginPage(request):
    cookies1=''
    cookies2=''
    if request.COOKIES.get('user'):
        cookies1=request.COOKIES['user']
        cookies2=request.COOKIES['upass']
    print('cooksdmfnsd,',cookies1,' ',cookies2)
    if request.method == 'POST':
        # username = request.POST.get('username',None)
        email = request.POST.get('email', None)
        print(email)
        password = request.POST.get('password', None)
        print(password)
        remember_me=None
        # remember_me = request.POST.get('remember_me', None)
        # print('remember_me', remember_me)
        # if username is not None and password is not None:
        if email is not None and password is not None:
            print('asd')
            # user = authenticate(request, username=username, password=password)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                print('login sus')
                if remember_me != None:
                    request.session.set_expiry(60 * 60 * 24 * 30 * 365)
                    # response = HttpResponse()
                    response = HttpResponseRedirect(reverse_lazy('customadmin:home'))
                    # response[email] = password
                    response.set_cookie('user', email)
                    response.set_cookie('upass', password)
                    return response
                if request.user.is_superuser:
                    return HttpResponseRedirect(reverse_lazy('customadmin:home'))
                # if request.user.role=="T":  
                #     return HttpResponseRedirect(reverse_lazy('tenat:home'))
                else:
                    return HttpResponseRedirect(reverse_lazy('employe:home'))

            messages.error(request, 'Username and password is Invalid')
    return render(request, 'registration/login.html', {'user': request.user,'cookies1':cookies1,'cookies2':cookies2})


def forgetpassword(request):
    form = ResetPasswordForm()
    msg = 'Enter your email and we will send you instructions to reset your password'
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        email = request.POST.get('forgot-password-email')
        # email = request.POST.get('email')
        # print(print'the email is',email)
        if (CustomUser.objects.filter(email=email).exists()):
            email = CustomUser.objects.get(email=email)
            token = get_random_string(16)
            # print('token is',token)
            ForgetPassMailVerify(user_id=email.id, link=token).save()
            # token = 'http://127.0.0.1:8000/user/forgetpassword/' + token
            token ='http://'+str(get_current_site(request).domain)+'/user/forgetpassword/' + token
            # print('the whole url is ',token)

            email_send(token, email,email_message='Please verify your email for changing the password',email_subject='Reset Password')
            msg = 'The activation link has been send to your Email.'
            messages.success(request,msg)
        else:
            messages.error(request, 'email is not exists')
        # print('the email is', email)

    # return render(request,'user_basic.html')
    return render(request, 'registration/password_reset.html',
                  {'form': form, 'msg': msg})
    # return render(request, 'html/ltr/vertical-menu-template/page-auth-forgot-password-v1.html',
    #               {'form': form, 'msg': msg})


def email_send(token, email,email_message,email_subject):
    # send_mail(
    #     email_subject,
    #     email_message +' '+ token,
    #     # 'radiantinfonet901@gmail.com',
    #     # 'mohdkaif@radiantinfonet.com',
    #     # 'support@radiantinfonet.com',
    #     # 'admin@navankur.org',
    #     'support@navankur.org',
    #     # 'kkaifkhan1040@gmail.com',
    #     [email],  #target email
    #     # fail_silently=False,
    # )
    email = EmailMessage(
    email_subject,
    email_message +' '+ token,
    'support@navankur.org',
    [email],
    # from_email='mohdkaif@radiantinfonet.com',
    headers={'Message-ID': '1'},
    
)
    email.send(fail_silently=False)

# def email_send(token, email,email_message,email_subject):
#     send_mail(
#         'Reset Password',
#         'Please click on the link to confirm your registration,  ' + token,
#         'support@navankur.org',
#         [email],
#         # fail_silently=False,
#     )


def create_password(request, id):
    if request.method == 'POST':
        password = request.POST.get('reset-password-new')
        con_pass = request.POST.get('reset-password-confirm')
        print(password,con_pass,len(password))
        if password == con_pass:
            try:
                change_pass = CustomUser.objects.get(id=id)
                change_pass.set_password(password)
                change_pass.save()
                messages.success(request, 'Password change successfully')
            except error as e:
                print(e)
            return redirect('customadmin:user_list')
        else:
            messages.error(request, 'Password not match')
    return redirect('customadmin:user_list')


# def changepassword(request):
#     print(request.method)
#     if request.method == "POST":
#         oldpass = CustomUser.objects.get(email=request.user)
#         print('oldpass:', oldpass.password)
#         password = request.POST.get('password')
#         new_password = request.POST.get('new-password')
#         confirm_password = request.POST.get('confirm-new-password')
#         print('pass:', password, "new:", new_password, 'con:', confirm_password)
#         if (new_password == confirm_password):
#             print('enter pass')
#             if (check_password(password, oldpass.password)):
#                 print('old pass')
#                 oldpass.set_password(new_password)
#                 oldpass.save()
#                 messages.success(request, 'Password change successfully')
#             else:
#                 messages.error(request, 'Old password not found')
#         return redirect('/admin/page_account')
#     return redirect('/admin/page_account')

def userverify(request, id):
    if (UserEmailVerify.objects.filter(link=id).exists()):
        obj = UserEmailVerify.objects.get(link=id)
        obj.verify = True
        obj.save()
        obj1 = CustomUser.objects.get(email=obj.user.email)
        msg = 'Once your profile is approved, we will notify you, and you will be able to log in.'
        # if obj1.role=="T":
        #     obj1.is_active = True
        #     obj1.save()
        #     msg='Email verified successfully Please login'
        messages.success(request, msg)
    return redirect('user:login')

def autologin(request,id):
    if CustomUser.objects.filter(token=id).exists():
        token=CustomUser.objects.get(token=id)
        user = authenticate(request, email=token.email, password=token.strpass)
        if user is not None:
            login(request, user)
    return redirect('customadmin:home')

import math, random
 
def numberverify(request):
    pass
#     comp=Company.objects.get(email=request.user)
#     if request.method=='POST':
#         print('post')
#         num=request.POST.get('contact_number')
#         print(num)
#         if comp.contact_number==num:
#             print('pass num')
#             digits = "0123456789"
#             OTP = ""
#             for i in range(6) :
#                 OTP += digits[math.floor(random.random() * 10)]
#             num_otp=UserNumberVerify.objects.get(user=comp.email)
#             msg=f'Your OTP is {OTP} - Radiant Infonet Pvt Ltd.'
#             resp = sendSMS('uwzHce7RY0U-128POV4LNe7NQ1heH6QCdIeRhkONA0', '91'+str(num),
#                 'RADPVT ',msg)
#             num_otp.otp=OTP
#             num_otp.save()
#             print('otp')
#             return redirect('/user/otpverify/')
#     return render(request,'registration/numverify.html',{'user':comp})

def otpverify(request):
    pass
#     if UserNumberVerify.objects.filter(user=request.user).exists():
#         number=UserNumberVerify.objects.get(user=request.user)
#         if request.method=="POST":
#             otp=request.POST.get('otp_number')
#             if number.otp==otp:
#                 number.verify=True
#                 number.save()
#                 messages.success(request,'OTP verified successfully')
#                 return redirect('customadmin:home')
#             messages.error(request,'Invalid OTP ')
#         return render(request,'registration/otpverify.html')
#     return redirect('customadmin:home')