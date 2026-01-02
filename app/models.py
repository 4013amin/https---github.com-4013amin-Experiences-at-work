from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    description = models.TextField(null = True , blank=True)

    def __str__(self):
        return self.user.username


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.username}: {self.code}"


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    offer = models.BooleanField(default=False)


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    code_offer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

