from django.contrib import admin
from .models import *
from django_json_widget.widgets import JSONEditorWidget
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from jsonfield import JSONField
from import_export.admin import ExportActionMixin
from import_export import resources





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
    search_fields = ['user__mobile', 'brand_name', 'register_number','user__email']
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    def mobile(self,instance):
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
    search_fields = ['title','unit']


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
    list_filter = ['supplier','sub_category','prod_type','sub_category__category']

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
        'user', 'product','mobile'
    ]
    search_fields = ['user__mobile','user__email']
    list_filter = ['product__sub_category','product__prod_type','product__supplier']

    def mobile(self,instance):
        return instance.user.mobile

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'mobile','product','rate','recommend','disable','created_at'
    ]
    search_fields = ['user__mobile','user__email']
    list_filter = ['disable','product__sub_category','product__prod_type','product__supplier']

    def mobile(self,instance):
        return instance.user.mobile




@admin.register(QuestionAndAnswer)
class QuestionAndAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'mobile','product','disable','created_at'
    ]
    search_fields = ['user__mobile','user__email']
    list_filter = ['disable','product__sub_category','product__prod_type','product__supplier']

    def mobile(self,instance):
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
        fields = ['qr_number', 'user__email', 'user__mobile','test','total_price','deliver_time',
                  'location',
                  'address',
                  'province',
                  'product'

                  ]
        export_order = ('qr_number', 'user__email', 'user__mobile', 'product')

    def dehydrate_product(self,order):
        invoices = Invoice.objects.filter(order=order).all()
        product = ' '
        for item in invoices:
            product += f'\n qty: {item.quantity} title: {item.product.name}'

        return product





@admin.register(Order)
class OrderAdmin(ExportActionMixin,admin.ModelAdmin):
    resource_class = OrderResource
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
    search_fields = ['id','qr_number','user__email','user__mobile']
    list_filter = ['is_archive','is_succeed',
                   'created_at',
                   'scheduling__location__province',
                   ['scheduling__deliver_date_time',DateTimeRangeFilter],
                   ]
    def mobile(self,instance):
        return instance.user.mobile



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
