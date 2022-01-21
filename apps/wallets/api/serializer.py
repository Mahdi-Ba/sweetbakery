from rest_framework import serializers
from ..models import *


class WalletSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=None)

    class Meta:
        model = Wallet
        fields = '__all__'


class DepositSerializer(serializers.ModelSerializer):
    amount = serializers.CharField(required=False)

    class Meta:
        model = Transaction
        fields = '__all__'


class WithdrawSerializer(serializers.ModelSerializer):
    amount = serializers.CharField(required=False)

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionResponse(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
