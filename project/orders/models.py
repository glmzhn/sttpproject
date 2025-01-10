import uuid
from django.db import models


# Model of The Product
class Product(models.Model):
    product_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


# Model of The Order
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    customer_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.order_id}"
