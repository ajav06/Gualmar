from django.contrib import admin

from core.models import User, Address

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'location', 'city', 'address')


admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
