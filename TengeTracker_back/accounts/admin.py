from django.contrib import admin

# Register your models here.
from .models import Wallet, Category, Transaction

admin.site.register(Wallet)
admin.site.register(Category)
admin.site.register(Transaction)
