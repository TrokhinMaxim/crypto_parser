from django.contrib import admin
from .models import Transactions


class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'sender', 'balance', 'wallet', 'date', 'crypto_name')
    search_fields = ('receiver', 'sender', 'wallet')
    list_filter = ('date',)

admin.site.register(Transactions, TransactionsAdmin)
