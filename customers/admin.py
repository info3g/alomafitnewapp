from django.contrib import admin

from customers.models import *


# Register your models here.
class AdminProfile(admin.ModelAdmin):
    readonly_fields = ['customer', 'id', ]


class AdminCustomer(admin.ModelAdmin):
    readonly_fields = ['user', 'slug']


admin.site.register(Customer, AdminCustomer)
admin.site.register(Profile, AdminProfile)
