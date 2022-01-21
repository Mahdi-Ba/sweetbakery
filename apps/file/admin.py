from django.contrib import admin

# Register your models here.
from apps.file.models import File


@admin.register(File)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id','file']