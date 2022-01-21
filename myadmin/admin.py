from django.contrib import admin
from django.utils.translation import gettext_lazy


class MyAdminSite(admin.AdminSite):
    enable_nav_sidebar = False
    site_title = gettext_lazy('Pec')

    site_header = gettext_lazy('Pec administration')

    index_title = gettext_lazy('Site administration')

