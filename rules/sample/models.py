from django.db import models

class Product(models.Model):
    product_type = models.CharField(max_length=20)
    stock = models.IntegerField()
    status = models.IntegerField()

    def __repr__(self):
        return "Product %s" % self.product_type

    def __str__(self):
        return self.__repr__()
