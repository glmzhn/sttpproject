import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order

# Получаем логгер
logger = logging.getLogger('order_activity')


# Логируем создание нового заказа
@receiver(post_save, sender=Order)
def log_order_creation(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Order created: {instance.order_id}, User: {instance.user.username}, Total Price: {instance.total_price}")


# Логируем обновление заказа
@receiver(post_save, sender=Order)
def log_order_update(sender, instance, created, **kwargs):
    if not created:  # Это обновление, а не создание
        logger.info(f"Order updated: {instance.order_id}, User: {instance.user.username}, Total Price: {instance.total_price}")


# Логируем удаление заказа
@receiver(post_delete, sender=Order)
def log_order_deletion(sender, instance, **kwargs):
    logger.info(f"Order deleted: {instance.order_id}, User: {instance.user.username}, Total Price: {instance.total_price}")
