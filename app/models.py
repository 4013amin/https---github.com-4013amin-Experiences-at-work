from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        expiration_time = self.created_at + timedelta(minutes=5)
        return timezone.now() < expiration_time

    def __str__(self):
        return f"OTP for {self.user.username}: {self.code}"


class Product(models.Model):
    image = models.ImageField(upload_to="products/")
    title = models.CharField(max_length=100)
    description = models.TextField()
    count = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    offer = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Products"


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    code_offer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cart"
