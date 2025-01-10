from django.contrib import admin
from .models import Order, Product

# Models for Admin Panel
admin.site.register(Order)
admin.site.register(Product)
