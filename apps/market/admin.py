from django.contrib import admin
from .models import *
from django_json_widget.widgets import JSONEditorWidget

from jsonfield import JSONField



@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'brand_name',
        'register_number',
        'address',
        'state',
    ]
    search_fields = ['user__mobile', 'brand_name', 'register_number']
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


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
    search_fields = ['title']


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
        'name',
        'part_number',
        'sub_category',
        'prod_type',
        'price',
    ]
    search_fields = [
        'supplier__brand_name',
        'name',
        'part_number'
    ]


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
        'user', 'product'
    ]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'rate',
        'product',
        'comment',
        'recommend',
        'disable',
        'created_at',
    ]
    search_fields = ['user__mobile', ]


@admin.register(QuestionAndAnswer)
class QuestionAndAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'user',
        'question',
        'answer',
        'created_at',
        'disable',

    ]
    search_fields = ['user__mobile', ]


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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [InvoiceModel]
    list_display = [
        'user',
        'scheduling',
        'total_price',
        'is_succeed',
        'is_archive',
        'updated_at',
        'qr_number',
    ]
    search_fields = ['id','qr_number','user__email','user__mobile']
    list_filter = ['created_at','is_archive']



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
