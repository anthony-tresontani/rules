from django.db import models

class Product(models.Model):
    product_type = models.CharField(max_length=20)
