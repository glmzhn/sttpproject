from django.core.cache import cache
import os
import logging


# Creating Cache Function
def delete_cache(key_prefix: str):
    # Connecting to The Redis
    redis_client = cache.client.get_client()
    # Creating Cache Keys
    cache_keys = redis_client.keys(f":1:views.decorators.cache.cache_page.{key_prefix}*")
    for key in cache_keys:
        # Deleting Cache by The Keys
        redis_client.delete(key)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "events.log")

# Настраиваем логгер
event_logger = logging.getLogger("event_stub")
event_logger.setLevel(logging.INFO)

# Добавляем обработчик для записи в файл
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
event_logger.addHandler(file_handler)


def send_order_status_change_event(order_id, old_status, new_status):
    """
    Логирует событие изменения статуса заказа.
    :param order_id: ID заказа
    :param old_status: Старый статус
    :param new_status: Новый статус
    """
    event_logger.info(
        f"Order {order_id} changed status from '{old_status}' to '{new_status}'"
    )
