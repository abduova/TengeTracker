from django.contrib import admin

# Register your models here.
from .models import Wallet, Category

admin.site.register(Wallet)
admin.site.register(Category)
