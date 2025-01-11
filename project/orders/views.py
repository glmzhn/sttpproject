from django.http import JsonResponse
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .middleware import MetricsMiddleware
from .models import Order
from .serializers import OrderSerializer
from .utils import delete_cache


# Returns The Metrics
def metrics_view(request):
    metrics = MetricsMiddleware.get_metrics()
    return JsonResponse(metrics)


# Timeout of The Cache
CACHE_TIMEOUT = 60 * 15  # 15 Minutes


# ModelViewSet for The Order Model
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.filter(is_deleted=False)
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # Creating Keys for The Cache
    KEY_PREFIX = 'orders-viewset'

    # Filter's Settings
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['status', 'customer_name']
    ordering_fields = ['total_price']

    # Processing Filters in The URL '/?status=<EXAMPLE>&min_price=<EXAMPLE>&max_price=<EXAMPLE>'
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if status:
            queryset = queryset.filter(status=status)

        if min_price:
            queryset = queryset.filter(total_price__gte=min_price)

        if max_price:
            queryset = queryset.filter(total_price__lte=max_price)

        return queryset

    # Decorator for Creating the Cache
    @method_decorator(cache_page(CACHE_TIMEOUT, key_prefix=KEY_PREFIX))
    # Processing GET Methods
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Processing DELETE Methods
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        delete_cache(self.KEY_PREFIX)
        return Response(status=status.HTTP_200_OK)
