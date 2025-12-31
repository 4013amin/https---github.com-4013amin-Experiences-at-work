from django.shortcuts import render
from . import forms 
from . import models
import random
from django.utils import timezone 
from datetime import timedelta


# Create your views here.
def register(request):

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            phone = form.cleaned_data['phone']
            description = form.cleaned_data['description']

            if models.User.objects.filter(username=username).exists():
                form.add_error('username', 'این نام کاربری قبلاً انتخاب شده است.')
                return render(request, 'auth/register_otp.html', {'form': form})

            if models.Profile.objects.filter(phone=phone).exists():
                form.add_error('phone', 'این شماره تلفن قبلاً ثبت شده است.')
                return render(request, 'auth/register_otp.html', {'form': form})

            user_instance = models.User.objects.create_user(username=username)
            profile = models.Profile.objects.create(
                user=user_instance,
                phone=phone,
                description=description
            )

            profile.save()
            return render(request, 'otp_success.html', {'username': username})
    else:
        form = forms.RegisterForm()
    context = {'form': form}
    return render(request, 'auth/register.html' , context)


def otp_request_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        try:
            profile = models.Profile.objects.get(phone=phone)
            models.OTP.objects.filter(user=profile.user).delete()
            code = str(random.randint(100000, 999999))
            otp = models.OTP.objects.create(user=profile.user, code=code)
            otp.save()

            #send_SMS

            print(f"OTP for {profile.user.username}: {code}")
            return render(request, 'auth/verify_otp.html', {'phone': phone})
           
        except models.Profile.DoesNotExist:
            form = forms.regiter_otp()
            form.add_error('phone', 'شماره تلفن یافت نشد. لطفاً ابتدا ثبت نام کنید.')
            return render(request, 'auth/verify_otp.html', {'form': form})
    else:
        form = forms.regiter_otp()
    return render(request, 'auth/register_otp.html', {'form': form})


def otp_verify_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('code')
        try:
            profile = models.Profile.objects.get(phone=phone)
            otp = models.OTP.objects.filter(user=profile.user, code=code).first()
            if otp:
                if otp.created_at < timezone.now() - timedelta(minutes=2):
                    otp.delete()
                    form = forms.verify_otp(request.POST)
                    form.add_error('code', 'کد منقضی شده است. لطفاً مجدداً تلاش کنید.')
                    return render(request, 'auth/verify_otp.html', {'form': form, 'phone': phone})

                otp.delete()
                login(request, profile.user)

                return render(request, 'otp_success.html', {'username': profile.user.username})
            else:
                form = forms.verify_otp(request.POST)
                form.add_error('code', 'کد تایید نادرست است. لطفاً مجدداً تلاش کنید.')
                return render(request, 'auth/verify_otp.html', {'form': form, 'phone': phone})
        except models.Profile.DoesNotExist:
            form = forms.verify_otp(request.POST)
            form.add_error('phone', 'شماره تلفن یافت نشد. لطفاً ابتدا ثبت نام کنید.')
            return render(request, 'auth/verify_otp.html', {'form': form, 'phone': phone})
    else:
        form = forms.verify_otp()
        return render(request, 'auth/verify_otp.html', {'form': form})