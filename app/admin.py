from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone')
    search_fields = ('phone', 'user__username')

@admin.register(models.OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__username', 'code')
    readonly_fields = ('created_at',)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']