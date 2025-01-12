import uuid
from django.contrib.auth.models import User
from django.db import models
from .utils import send_order_status_change_event


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.order_id:
            old_status = None
        else:
            try:
                old_status = Order.objects.get(order_id=self.order_id).status
            except Order.DoesNotExist:
                old_status = None

        # Сохраняем объект заказа
        super().save(*args, **kwargs)

        # Если старый статус существует и отличается от нового, выбрасываем событие
        if old_status and old_status != self.status:
            send_order_status_change_event(
                order_id=self.order_id,
                old_status=old_status,
                new_status=self.status
            )

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
