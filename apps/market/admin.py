from django.contrib import admin
from .models import *
from django_json_widget.widgets import JSONEditorWidget
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from jsonfield import JSONField
from import_export.admin import ExportActionMixin
from import_export import resources
from django.contrib.admin import helpers
from django.shortcuts import render
from django.db import connection
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
import xlwt
from datetime import datetime


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'mobile',
        'brand_name',
        'register_number',
        'address',
        'state',
    ]
    search_fields = ['user__mobile', 'brand_name', 'register_number', 'user__email']
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def mobile(self, instance):
        return instance.user.mobile


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]
    search_fields = ['name']


#
# @admin.register(PerforamRequest)
# class PerformaAdmin(admin.ModelAdmin):
#     list_display = [
#         'id','order_id','user','supplier'
#     ]
#
#     def user(self,instance):
#         return instance.order.user
#
#     def order_id(self,instance):
#         return instance.order.id
#
#     def supplier(self,instance):
#         return instance.invoice.first().product.supplier


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'unit',
    ]
    search_fields = ['title', 'unit']


class ProductSpecificationModel(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ProductImagesModel(admin.TabularInline):
    model = ProductImages
    extra = 1


class DiscountModel(admin.TabularInline):
    model = Discount
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSpecificationModel, ProductImagesModel, DiscountModel]

    list_display = [
        'supplier',
        # 'mobile',
        # 'email',
        'name',
        'part_number',
        'sub_category',
        'prod_type',
        'price',
    ]
    search_fields = [
        'supplier__brand_name',
        'supplier__user__mobile',
        'supplier__user__email',
        'name',
        'part_number'
    ]
    list_filter = ['supplier', 'sub_category', 'prod_type', 'sub_category__category']

    # def mobile(self,instance):
    #     return instance.supplier.user.mobile
    #
    # def email(self,instance):
    #     return instance.supplier.user.email


class SubCategoryModel(admin.TabularInline):
    model = SubCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryModel]
    list_display = [
        'name',
    ]
    search_fields = ['name']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product', 'mobile'
    ]
    search_fields = ['user__mobile', 'user__email']
    list_filter = ['product__sub_category', 'product__prod_type', 'product__supplier']

    def mobile(self, instance):
        return instance.user.mobile


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'mobile', 'product', 'rate', 'recommend', 'disable', 'created_at'
    ]
    search_fields = ['user__mobile', 'user__email']
    list_filter = ['disable', 'product__sub_category', 'product__prod_type', 'product__supplier']

    def mobile(self, instance):
        return instance.user.mobile


@admin.register(QuestionAndAnswer)
class QuestionAndAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'mobile', 'product', 'disable', 'created_at'
    ]
    search_fields = ['user__mobile', 'user__email']
    list_filter = ['disable', 'product__sub_category', 'product__prod_type', 'product__supplier']

    def mobile(self, instance):
        return instance.user.mobile


# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = [
#         'user',
#         'is_read',
#         'created_at',
#     ]
#     search_fields = ['user__mobile', ]
#
#
# @admin.register(NotificationDescription)
# class NotificationDescriptionAdmin(admin.ModelAdmin):
#     list_display = [
#         'type_of_notification',
#         'description',
#     ]


class InvoiceModel(admin.TabularInline):
    model = Invoice
    extra = 1


from import_export.fields import Field


class OrderResource(resources.ModelResource):
    product = Field()
    deliver_time = Field(attribute='scheduling__deliver_date_time', column_name='deliver_time')
    location = Field(attribute='scheduling__location__title', column_name='location')
    address = Field(attribute='scheduling__location__address', column_name='address')
    province = Field(attribute='scheduling__location__province__title', column_name='province')

    # location = Field()

    class Meta:
        model = Order
        fields = ['qr_number', 'user__email', 'user__mobile', 'test', 'total_price', 'deliver_time',
                  'location',
                  'address',
                  'province',
                  'product'

                  ]
        export_order = ('qr_number', 'user__email', 'user__mobile', 'product')

    def dehydrate_product(self, order):
        invoices = Invoice.objects.filter(order=order).all()
        product = ' '
        for item in invoices:
            product += f'\n qty: {item.quantity} title: {item.product.name}'

        return product

@admin.register(Invoice)
class InvoiceAdmin( admin.ModelAdmin):
    list_display = [
        'product',
        'order',
        'quantity',
        'price',
    ]
    search_fields = ['order__id']



@admin.register(Order)
class OrderAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = OrderResource
    actions = ['report_one', 'report_two']
    inlines = [InvoiceModel]
    list_display = [
        'user',
        'mobile',
        'scheduling',
        'total_price',
        'is_succeed',
        'is_archive',
        'created_at',
        'updated_at',
        'qr_number',
    ]
    search_fields = ['id', 'qr_number', 'user__email', 'user__mobile']
    list_filter = ['is_archive', 'is_succeed',
                   'created_at',
                   'scheduling__location__province',
                   ['scheduling__deliver_date_time', DateTimeRangeFilter],
                   ]
    readonly_fields = ('scheduling',)

    def mobile(self, instance):
        return instance.user.mobile

    def report_one(self, request, queryset):
        # if len(queryset) > 1:
        #     self.message_user(request, 'Please select only one record.', level=messages.ERROR)
        #     return HttpResponseRedirect(redirect_to=BASE_URL + '/admin/wallets/wallet/')
        #
        # wallet = queryset.first()
        if request.POST.get('apply', False):
            with connection.cursor() as cursor:
                cursor.execute("""
        select mp.id as product_id,mp.name as product_name,sum(market_invoice.quantity) total,gl.title as location,gp.title as city
             ,gs.deliver_date_time,gl.id from market_invoice inner join market_order mo on mo.id = market_invoice.order_id
                inner join general_scheduling gs on gs.id = mo.scheduling_id
                inner join market_product mp on mp.id = market_invoice.product_id
                inner join general_location gl on gl.id = gs.location_id
                inner join general_province gp on gl.province_id = gp.id
                where deliver_date_time >  %s and deliver_date_time <  %s
                group by mp.id,gl.id,gp.title, gs.deliver_date_time
                    """, [request.POST['date_time'], request.POST['end_date_time']])
                rows = cursor.fetchall()

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="report_one.xls"'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('tax')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['product_id', 'product_name', 'total','location','city', 'date']

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            for row in rows:
                row_num += 1
                ws.write(row_num, 0, row[0], font_style)
                ws.write(row_num, 1, row[1], font_style)
                ws.write(row_num, 2, row[2], font_style)
                ws.write(row_num, 3, row[3], font_style)
                ws.write(row_num, 4, row[4], font_style)
                ws.write(row_num, 5, row[5].strftime('%y/%m/%d'), font_style)
            wb.save(response)
            return response

        else:
            form = queryset
            context = dict(
                admin.site.each_context(request),
            )
            context['form'] = form
            context['action_checkbox_name'] = helpers.ACTION_CHECKBOX_NAME
            return render(
                request=request,
                template_name='adminpanel/report_one.html',
                context=context)

    def report_two(self, request, queryset):
        # if len(queryset) > 1:
        #     self.message_user(request, 'Please select only one record.', level=messages.ERROR)
        #     return HttpResponseRedirect(redirect_to=BASE_URL + '/admin/wallets/wallet/')
        #
        # wallet = queryset.first()
        if request.POST.get('apply', False):
            with connection.cursor() as cursor:
                cursor.execute("""
                    select mp.id as product_id,mp.name as product_name,sum(market_invoice.quantity) total
                         ,gs.deliver_date_time from market_invoice  inner join market_order mo on mo.id = market_invoice.order_id
                    inner join general_scheduling gs on gs.id = mo.scheduling_id
                    inner join market_product mp on mp.id = market_invoice.product_id
                    inner join general_location gl on gl.id = gs.location_id
                    inner join general_province gp on gl.province_id = gp.id
                    where deliver_date_time >  %s and deliver_date_time <  %s
                    group by mp.id,gs.deliver_date_time
                    """, [request.POST['date_time'], request.POST['end_date_time']])
                rows = cursor.fetchall()


            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="report_two.xls"'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('tax')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['product_id','product_name','total','date']

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            for row in rows:
                row_num += 1
                ws.write(row_num, 0, row[0], font_style)
                ws.write(row_num, 1, row[1], font_style)
                ws.write(row_num, 2, row[2], font_style)
                ws.write(row_num, 3,row[3].strftime('%y/%m/%d'), font_style)
            wb.save(response)
            return response

        else:
            form = queryset
            context = dict(
                admin.site.each_context(request),
            )
            context['form'] = form
            context['action_checkbox_name'] = helpers.ACTION_CHECKBOX_NAME
            return render(
                request=request,
                template_name='adminpanel/report_two.html',
                context=context)

# @admin.register(ProductTracking)
# class ProductTrackingAdmin(admin.ModelAdmin):
#     list_display = [
#         'order',
#         'product',
#         'track_location',
#     ]
#     formfield_overrides = {
#         JSONField: {'widget': JSONEditorWidget},
#     }
#
#
#
#
#
