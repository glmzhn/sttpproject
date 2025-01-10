from django.core.cache import cache


# Creating Cache Function
def delete_cache(key_prefix: str):
    # Connecting to The Redis
    redis_client = cache.client.get_client()
    # Creating Cache Keys
    cache_keys = redis_client.keys(f":1:views.decorators.cache.cache_page.{key_prefix}*")
    for key in cache_keys:
        # Deleting Cache by The Keys
        redis_client.delete(key)
