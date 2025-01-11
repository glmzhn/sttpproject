from rest_framework import serializers
from .models import Order, Product
from .utils import delete_cache


# ModelSerializer for The Product Model
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'quantity']


# ModelSerializer for The Order Model
class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    user = serializers.StringRelatedField()

    # Creating Keys for The Cache
    KEY_PREFIX = 'orders-viewset'

    class Meta:
        model = Order
        fields = ['order_id', 'user', 'status', 'total_price', 'products', 'is_deleted']

    # Processing POST Method
    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for product_data in products_data:
            product = Product.objects.create(**product_data)
            order.products.add(product)

        # Deleting Cache
        delete_cache(self.KEY_PREFIX)

        return order

    # Processing PUT/PATCH Methods
    def update(self, instance, validated_data):
        products_data = validated_data.pop('products', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if products_data:
            instance.products.clear()

            for product_data in products_data:
                product, created = Product.objects.get_or_create(**product_data)
                instance.products.add(product)

        delete_cache(self.KEY_PREFIX)
        return instance
