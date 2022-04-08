import uuid
from django.db import models
import jsonfield
from apps.file.models import File
from apps.general.models import Scheduling
from apps.users.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import qrcode


class State(models.IntegerChoices):
    accepted = 0, 'accepted'
    waiting = 1, 'waiting'
    rejected = 2, 'rejected'


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    factory_location = jsonfield.JSONField()
    brand_name = models.CharField(max_length=255, null=True, blank=True)
    register_number = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(max_length=1024, null=True, blank=True)
    description = models.TextField(max_length=1024, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to='brand/logo/')
    wallpaper = models.ImageField(null=True, blank=True, upload_to='brand/wallpaper/')
    state = models.IntegerField(choices=State.choices, default=State.accepted)

    def __str__(self):
        if self.brand_name is None:
            return 'No Name'
        return self.brand_name


class ProductType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    thumbnail = models.ImageField(null=True, blank=True, upload_to='category/thumbnail/')

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(Category, related_name='sub_category', null=True, on_delete=models.CASCADE)

    # is_active = models.BooleanField(default=False)
    # logo = models.ImageField(null=True, blank=True, upload_to='os/logo/')

    def __str__(self):
        return self.name


class Specification(models.Model):
    title = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Product(models.Model):
    supplier = models.ForeignKey(Supplier, null=True, on_delete=models.CASCADE)
    thumbnail = models.ImageField(null=True, blank=True, upload_to='product/thumbnail/')
    name = models.CharField(max_length=255)
    part_number = models.CharField(max_length=255)
    sub_category = models.ForeignKey(SubCategory, null=True, on_delete=models.DO_NOTHING)
    prod_type = models.ForeignKey(ProductType, null=True, on_delete=models.DO_NOTHING)
    # guarantee_description = models.CharField(max_length=255)
    # warranty_description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unlimited = models.BooleanField(default=False)
    price = models.IntegerField()
    extra_discount = models.BooleanField(default=False)
    extra_discount_percent = models.FloatField(blank=True, null=True, default=0)
    extra_discount_price = models.IntegerField(null=True)
    description = models.TextField(max_length=1024)
    video = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, related_name="product_video", blank=True)
    catalog = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, related_name="catalog", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    slider = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="product_specification")
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE, related_name="specification")
    number = models.CharField(max_length=255)


class ProductImages(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='product_images')
    picture = models.ImageField(null=True, blank=True, upload_to='product/picture/')


class Discount(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='product_discounts')
    upper_bound = models.IntegerField(blank=True, null=True)
    lower_bound = models.IntegerField(blank=True, null=True)
    percent = models.FloatField(blank=True, null=True)
    price = models.IntegerField()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)


class Rating(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    rate = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rate_obj')
    comment = models.TextField()
    recommend = models.BooleanField(default=True)
    disable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class QuestionAndAnswer(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    disable = models.BooleanField(default=False)


class NotificationType(models.IntegerChoices):
    SYSTEM = 0, 'System Notification'
    QUESTION = 1, 'New Question For A Product'
    QUESTION_ANSWER = 2, 'Question Answered'
    REVIEW = 3, 'New Review For A Product'
    CHANGE_ORDER = 4, 'Order Item Status Changed'
    NEW_ORDER = 5, 'New Order For A Product'


class NotificationDescription(models.Model):
    type_of_notification = models.IntegerField(choices=NotificationType.choices)
    description = models.TextField()


class Notification(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    notification_description = models.ForeignKey(NotificationDescription, on_delete=models.SET_NULL, null=True,
                                                 default=None)
    link = models.URLField(default=None)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)


class OrderStatus(models.IntegerChoices):
    ORDER = 0, 'Ordered Received'
    PROCESSING = 1, 'Ordered Processed'
    READY_TO_DELIVER = 2, 'Order Ready to Deliver'
    DELIVERED = 3, 'Delivered'


class Order(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    scheduling = models.ForeignKey(Scheduling, null=True, on_delete=models.CASCADE)
    qr_number = models.UUIDField(default=uuid.uuid4, editable=False)
    total_price = models.FloatField()
    products = models.ManyToManyField(Product, through='Invoice')
    is_succeed = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    email = models.EmailField()
    state = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.ORDER)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.id)


class Invoice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()
    is_purchase = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        unique_together = ('product', 'order')


class PerforamRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    invoice = models.ManyToManyField(Invoice)
    is_archive = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)


class ProductTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    track_location = jsonfield.JSONField()


@receiver(post_save, sender=Order)
def save_qr_code(sender, instance, **kwargs):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5)
    qr.add_data(instance.qr_number)
    qr.make(fit=True)
    img = qr.make_image(fill='white', back_color=(169, 127, 55))
    img.save(f'media/qr_code/{instance.qr_number}.png')



import os


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)


@receiver(post_delete, sender=Order)
def delete_file(sender, instance, *args, **kwargs):
    if instance.qr_number:
        _delete_file(f'media/qr_code/{instance.qr_number}.png')
