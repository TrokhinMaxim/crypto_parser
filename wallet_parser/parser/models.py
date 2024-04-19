from django.db import models

class Transactions(models.Model):
    receiver = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    balance = models.PositiveIntegerField()
    wallet = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    crypto_name = models.CharField(max_length=50, default='Unknown')

