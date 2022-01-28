from django.contrib import admin
from apps.general.models import *


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = [
        'title',
    ]
    search_fields = ['title']



@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['title', 'state']
    list_filter = [
        'state',
    ]
    search_fields = ['title']





@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['title', 'address','province']
    list_filter = ['province']
    search_fields = ['title']


from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

@admin.register(Scheduling)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['deliver_date_time', 'location','is_enable']
    list_editable = ['is_enable']
    search_fields = ['location__title']
    list_filter = (
        ('deliver_date_time',DateTimeRangeFilter),'location__province','is_enable'
    )








