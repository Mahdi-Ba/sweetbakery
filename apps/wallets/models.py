import uuid
from enum import Enum

from django.db import models

from apps.market.models import Order
from apps.users.models import User


class Wallet(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    free = models.DecimalField(max_digits=12, decimal_places=2)
    freeze = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)




class TransactionType(Enum):
    DEPOSIT = "Deposit"
    WITHDRAW = "Withdraw"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Transaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    number = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    title = models.CharField(null=True, max_length=250)
    description = models.CharField(null=True, max_length=250)
    type = models.CharField(max_length=32, choices=TransactionType.choices(), null=True)
    amount = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)


    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"



