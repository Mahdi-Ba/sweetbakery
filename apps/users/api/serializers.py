from django.contrib.auth.hashers import make_password
from django.db.models import Q
from ..models import User
from rest_framework import serializers
from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    first_name = serializers.CharField(max_length=200, required=False)
    last_name = serializers.CharField(max_length=200, required=False)
    password = serializers.CharField(max_length=200, required=False)
    email = serializers.EmailField(required=False)
    avatar = serializers.ImageField(required=False, allow_null=True)
    is_staff = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['mobile', 'phone_number', 'first_name', 'last_name', 'email', 'avatar', 'password','is_staff']

    def validate_email(self, value):
        if User.objects.filter(Q(email__exact=value) & ~Q(mobile=self.initial_data['mobile'])).count() > 0:
            raise serializers.ValidationError(_('Universally unique identifier'))
        return value

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.password = make_password(validated_data['password'])
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate_email(self, value):
        if User.objects.filter(Q(email__exact=value) & ~Q(mobile=self.initial_data['mobile'])).count() > 0:
            raise serializers.ValidationError(_('Universally unique identifier'))
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)
