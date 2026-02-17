from django.db import models


# Create your models here.

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=12)

    def __str__(self):
        return self.username


class Vendor_Profile(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    phone = models.CharField(max_length=12)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.user.name


class vendor_request(models.Model):
    phone = models.CharField(max_length=12)
    description = models.TextField()

    def __str__(self):
        return self.vendor.name
