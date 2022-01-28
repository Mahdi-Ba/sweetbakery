
from django.contrib import admin

from .models import Wallet, Transaction

#
# @admin.register(Wallet)
# class WalletAdmin(admin.ModelAdmin):
#
#     list_display = (
#         'id',
#         'user',
#         'free',
#         'freeze',
#         'total',
#         'created_at',
#         'updated_at',
#     )
#     list_filter = (
#         'created_at',
#         'updated_at',
#     )
#     date_hierarchy = 'updated_at'
#
#     def total(self,instance):
#         return instance.freeze + instance.free
#
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        'owner',
        'order',
        'number',
        'title',
        'type',
        'amount',
        'created_at',
    )
    list_filter = (
        ('created_at',DateTimeRangeFilter),
    )
    date_hierarchy = 'created_at'
    autocomplete_fields = ['order']
    search_fields = ['owner__mobile','number' ]

