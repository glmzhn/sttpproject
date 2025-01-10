from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, metrics_view

# API Router
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

# Routing Endpoints
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('metrics/', metrics_view, name='metrics'),
]
