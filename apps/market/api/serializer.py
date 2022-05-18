from django.db.models import Avg
from rest_framework import serializers

from ..models import *
from ...general.api.serializer import SchedulingSerializer
from ...users.api.serializers import UserSerializer


class SupplierRegisterSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.mobile')
    factory_location = serializers.JSONField()
    brand_name = serializers.CharField()
    register_number = serializers.CharField()
    address = serializers.CharField()

    class Meta:
        model = Supplier
        exclude = [
            'logo',
            'wallpaper',
            'state',
            'description'
        ]


class SupplierSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.mobile')

    class Meta:
        model = Supplier
        exclude = [
            'state'
        ]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        exclude = [
            'user',
            'state'
        ]


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(read_only=True, source='category.name')

    class Meta:
        model = SubCategory
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    sub_category = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = '__all__'


class ProductSupplierCreateSerializer(serializers.ModelSerializer):
    supplier = serializers.ReadOnlyField(source='supplier.brand_name')
    supplier_id = serializers.ReadOnlyField(source='supplier.id')
    slider = serializers.ReadOnlyField()
    url_video = serializers.ReadOnlyField(source='video.file.url')
    url_catalog = serializers.ReadOnlyField(source='catalog.file.url')
    sub_category_obj = SubCategorySerializer(read_only=True, source='sub_category')
    prod_type_obj = ProductTypeSerializer(read_only=True, source='prod_type')

    class Meta:
        model = Product
        fields = '__all__'

class QuestionAndAnswerShowSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = QuestionAndAnswer
        fields = '__all__'


class RatingShowSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = Rating
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = Favorite
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')
    rate = serializers.FloatField(min_value=0, max_value=5)

    class Meta:
        model = Rating
        exclude = [
            'disable',
        ]


class QuestionAndAnswerReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAndAnswer
        exclude = [
            'user',
            'question',
            'disable',
        ]


class AskQuestionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = QuestionAndAnswer
        exclude = [
            'answer',
            'disable',
        ]


class ProductSupplierShowSerializer(serializers.ModelSerializer):
    supplier = serializers.ReadOnlyField(source='supplier.brand_name')
    supplier_id = serializers.ReadOnlyField(source='supplier.id')

    url_video = serializers.ReadOnlyField(source='video.file.url')
    url_catalog = serializers.ReadOnlyField(source='catalog.file.url')
    sub_category_obj = SubCategorySerializer(read_only=True, source='sub_category')
    prod_type_obj = ProductTypeSerializer(read_only=True, source='prod_type')
    rate = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_rate(self, obj):
        return {'avg':
                    Rating.objects.filter(product_id=obj.id, disable=False).all().aggregate(Avg('rate'))['rate__avg']}


class ProductSpecificationCreateSerializer(serializers.ModelSerializer):
    specification_title = serializers.CharField(read_only=True, source='specification.title')
    specification_unit = serializers.CharField(read_only=True, source='specification.unit')

    class Meta:
        model = ProductSpecification
        fields = '__all__'


class ProductDiscountSerializer(serializers.ModelSerializer):
    upper_bound = serializers.IntegerField()
    lower_bound = serializers.IntegerField()
    percent = serializers.FloatField(min_value=0, max_value=100)
    price = serializers.IntegerField()

    class Meta:
        model = Discount
        fields = '__all__'


class ProductDiscountdeleteSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Discount
        fields = ['ids']


class ProductSpecificationdeleteSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = ProductSpecification
        fields = ['ids']


class ProductImagesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = '__all__'


class ProductImagesdeleteSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = ProductSpecification
        fields = ['ids']


class ProductSupplierDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.ReadOnlyField(source='supplier.brand_name')
    supplier_id = serializers.ReadOnlyField(source='supplier.id')
    url_video = serializers.ReadOnlyField(source='video.file.url')
    url_catalog = serializers.ReadOnlyField(source='catalog.file.url')
    sub_category_obj = SubCategorySerializer(read_only=True, source='sub_category')
    prod_type_obj = ProductTypeSerializer(read_only=True, source='prod_type')
    product_specification = ProductSpecificationCreateSerializer(many=True)
    product_images = ProductImagesCreateSerializer(many=True)
    product_discounts = ProductDiscountSerializer(many=True)
    rate = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_rate(self, obj):
        return {'avg':
                    Rating.objects.filter(product_id=obj.id, disable=False).all().aggregate(Avg('rate'))['rate__avg']}

    def get_is_like(self, obj):
        user = self.context.get('user', None)
        if user is None:
            return False
        if obj.id is None or obj.id == '':
            return False
        return Favorite.objects.filter(user__mobile=user, product_id=obj.id).exists()


class InvoiceSerilizer(serializers.ModelSerializer):
    invoice_id = serializers.IntegerField(source='id')
    product_obj = ProductSupplierDetailSerializer(source='product')
    is_purchase = serializers.ReadOnlyField()
    price = serializers.IntegerField()
    supplier = SupplierSerializer(source='product.supplier')

    class Meta:
        model = Invoice
        fields = ['invoice_id', 'quantity', 'price', 'is_purchase', 'supplier',
                  'product_obj', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.mobile')
    total_price = serializers.ReadOnlyField()
    products = InvoiceSerilizer(source='invoice_set', read_only=True, many=True)
    scheduling = SchedulingSerializer(read_only=True, many=False)
    is_succeed = serializers.ReadOnlyField()
    is_archive = serializers.ReadOnlyField()
    is_locked = serializers.ReadOnlyField()
    qr_number = serializers.ReadOnlyField()
    state = serializers.IntegerField()
    custom_address =  serializers.CharField(max_length=256,allow_blank=True, default='')
    state_name = serializers.CharField(source='get_state_display')

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'scheduling',
            'total_price',
            'custom_address',
            'products',
            'is_succeed',
            'is_archive',
            'is_locked',
            'updated_at',
            'state', 'state_name', 'qr_number'

        ]


class CardInformationSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
    card_number = serializers.CharField(required=True)
    expiration_date = serializers.CharField(required=True)
    card_code = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    company = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    zip = serializers.CharField(required=True)
    country = serializers.CharField(required=True)


class OrderRequestSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField(source='user.mobile')

    class Meta:
        model = Order
        fields = '__all__'


class NotificationDescriptionSerializer(serializers.ModelSerializer):
    type_of_notification_title = serializers.CharField(source='get_type_of_notification_display')

    class Meta:
        model = NotificationDescription
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    notification_description = NotificationDescriptionSerializer(many=False)

    class Meta:
        model = Notification
        fields = '__all__'


class UpdateSiteNotificationSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Notification
        fields = ['ids']


class PerforamRequestSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerilizer(many=True)
    # user = UserSerializer(source='order.user')
    full_name = serializers.ReadOnlyField(source='order.full_name')
    phone = serializers.ReadOnlyField(source='order.phone')
    email = serializers.ReadOnlyField(source='order.email')
    address = serializers.ReadOnlyField(source='order.address')
    postal_code = serializers.ReadOnlyField(source='order.postal_code')
    location = serializers.ReadOnlyField(source='order.location')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = PerforamRequest
        fields = '__all__'

    def get_total_price(self, instance):
        price = 0
        for item in instance.invoice.all():
            price += item.quantity * item.price
        return price


class PerforamRequestSerializerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerforamRequest
        fields = '__all__'


class InvoiceSupplierSerilizer(serializers.ModelSerializer):
    invoice_id = serializers.IntegerField(source='id')
    product_obj = ProductSupplierDetailSerializer(source='product')
    is_purchase = serializers.ReadOnlyField()
    price = serializers.IntegerField()
    # state = serializers.IntegerField()
    # state_name = serializers.CharField(source='get_state_display')
    total_price = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='order.full_name')
    phone = serializers.CharField(source='order.phone')
    email = serializers.EmailField(source='order.email')
    address = serializers.CharField(source='order.address')
    postal_code = serializers.EmailField(source='order.postal_code')
    location = serializers.JSONField(source='order.location')

    class Meta:
        model = Invoice
        fields = ['invoice_id', 'quantity', 'price', 'is_purchase', 'total_price',
                  'product_obj', 'updated_at', 'full_name', 'phone', 'email', 'address', 'postal_code', 'location',

                  ]

    def get_total_price(self, instance):
        return instance.quantity * instance.price


class InvoiceStateSerilizer(serializers.Serializer):
    state = serializers.ChoiceField(OrderStatus.choices)


class InvoiceRequestCreateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required=True)
    order = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = '__all__'
