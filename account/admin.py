from django.contrib import admin

from .models import Account_Type, Account_Base

class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('login', 'label', 'aktiv', 'type',)
    search_fields = ('login', 'label', 'aktiv', 'type')

class AccountBaseAdmin(admin.ModelAdmin):
    list_display = ('login', 'account_type', 'account_amount', 'account_info',)
    search_fields = ('login', 'account_type',)

admin.site.register(Account_Type, AccountTypeAdmin)
admin.site.register(Account_Base, AccountBaseAdmin)
