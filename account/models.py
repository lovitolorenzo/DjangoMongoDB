from djongo import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    random_given = models.FloatField()
    starting_balance = models.FloatField(default=0.00)
    balance = models.FloatField(default=0.00)
    BitCoin = models.FloatField(default=0.00)


class Order(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    datetime = models.DateTimeField(blank=True, null=True)
    pending = models.BooleanField(default=True)
    class Meta:
        abstract = True


class Buy(Order):
    offer = models.FloatField()
    demand_quantity = models.FloatField()
    on_blockchain = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, unique=True)


class Sell(Order):
    selling_price = models.FloatField()
    selling_quantity = models.FloatField()
    on_blockchain = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, unique=True)
