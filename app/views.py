from django.shortcuts import render, redirect, get_object_or_404
from . import forms 
from . import models
import random
from django.utils import timezone 
from datetime import timedelta
from django.contrib.auth import login , logout
from django.contrib.auth.decorators import login_required

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
                return render(request, 'auth/register.html', {'form': form})

            if models.Profile.objects.filter(phone=phone).exists():
                form.add_error('phone', 'این شماره تلفن قبلاً ثبت شده است.')
                return render(request, 'auth/register.html', {'form': form})

            user_instance = models.User.objects.create_user(username=username)
            profile = models.Profile.objects.create(
                user=user_instance,
                username =username,
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
        form = forms.regiter_otp(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            try:
                profile = models.Profile.objects.get(phone=phone)

                models.OTP.objects.filter(user=profile.user).delete()
                code = str(random.randint(100000, 999999))
                otp = models.OTP.objects.create(user=profile.user, code=code)

                print(f"OTP for {profile.user.username}: {code}")
                #Send_SMS

                verify_form = forms.verify_otp(initial={'phone': phone})
                return render(request, 'auth/verify_otp.html', {'form': verify_form, 'phone': phone})

            except models.Profile.DoesNotExist:
                form.add_error('phone', 'شماره تلفن یافت نشد. لطفاً ابتدا ثبت نام کنید.')

                return render(request, 'auth/register_otp.html', {'form': form})
        else:
            return render(request, 'auth/register_otp.html', {'form': form})

    else:
        form = forms.regiter_otp()
    return render(request, 'auth/register_otp.html', {'form': form})


def otp_verify_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = request.POST.get('code')
        try:
            profile = models.Profile.objects.get(phone=phone)
            otp = models.OTP.objects.filter(user=profile.user, code=code).last()
            
            if otp:
                if otp.created_at < timezone.now() - timedelta(minutes=2):
                    otp.delete()
                    form = forms.verify_otp(request.POST)
                    form.add_error('code', 'کد منقضی شده است. لطفاً مجدداً تلاش کنید.')
                    return render(request, 'auth/verify_otp.html', {'form': form, 'phone': phone})

                otp.delete()
                
                login(request, profile.user)
                return redirect('home')

            else:
                form = forms.verify_otp(request.POST)
                form.add_error('code', 'کد تایید نادرست است. لطفاً مجدداً تلاش کنید.')
                return render(request, 'auth/verify_otp.html', {'form': form, 'phone': phone})
                
        except models.Profile.DoesNotExist:
            form = forms.regiter_otp()
            form.add_error('phone', 'شماره تلفن یافت نشد. لطفاً ابتدا ثبت نام کنید.')
            return render(request, 'auth/register_otp.html', {'form': form})
    else:
        form = forms.verify_otp()
        return render(request, 'auth/verify_otp.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('otp_request')



@login_required(login_url='otp_request')
def home(request):
    categories = models.Category.objects.all()
    products = models.Product.objects.filter(is_best_seller = True)
    some_product = models.Product.objects.filter(is_best_seller = False)

    context = {'categories': categories , 'products': products , 'some_product': some_product}
    return render(request, 'home/home.html' , context)


@login_required(login_url='otp_request')
def product_list(request):
    products = models.Product.objects.all()
    categories = models.Category.objects.all()

    context = {'products': products , 'categories': categories}

    return render(request, 'home/product_list.html' , context)


def product_detail(request, pk):
    products = get_object_or_404(models.Product, pk=pk)
    context = {'product_detail': products}
    return render(request, 'home/product_detail.html' , context)


def cart(request):
    return render(request, 'home/cart.html')

def checkout(request):
    return render(request, 'home/checkout.html')