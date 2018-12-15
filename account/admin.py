from django.contrib import admin

from .models import Account_Type, Account_Base, Account, Account_Pos

class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('login', 'label', 'aktiv', 'type',)
    search_fields = ('login', 'label', 'aktiv', 'type')

class AccountBaseAdmin(admin.ModelAdmin):
    list_display = ('login', 'account_type', 'account_amount', 'account_info',)
    search_fields = ('login', 'account_type',)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('login', 'account_type', 'account_year', 'account_month', 'account_amount',)
    search_fields = ('login', 'account_year', 'account_month',)

class AccountPosAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'pos', 'booking_amount', 'booking_info')


admin.site.register(Account_Type, AccountTypeAdmin)
admin.site.register(Account_Base, AccountBaseAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Account_Pos, AccountPosAdmin)
