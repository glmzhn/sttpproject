from django.http import JsonResponse
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .middleware import MetricsMiddleware
from .models import Order
from .serializers import OrderSerializer
from .utils import delete_cache
from rest_framework.permissions import IsAuthenticated, BasePermission


# Returns The Metrics
def metrics_view(request):
    metrics = MetricsMiddleware.get_metrics()
    return JsonResponse(metrics)


# Timeout of The Cache
CACHE_TIMEOUT = 60 * 15  # 15 Minutes


# Custom Permisson Class for Admins
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return obj.user == request.user


# ModelViewSet for The Order Model
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.filter(is_deleted=False)
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    # Creating Keys for The Cache
    KEY_PREFIX = 'orders-viewset'

    # Filter's Settings
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['status', 'user']
    ordering_fields = ['total_price']

    # Processing Filters in The URL '/?status=<EXAMPLE>&min_price=<EXAMPLE>&max_price=<EXAMPLE>'
    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_staff:  # Admin Can See All The Orders
            return queryset

        status = self.request.query_params.get('status')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if status:
            queryset = queryset.filter(status=status)
        if min_price:
            queryset = queryset.filter(total_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(total_price__lte=max_price)

        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Setting Current User as an Order's Owner
        serializer.save(user=self.request.user)

    def dispatch(self, *args, **kwargs):
        # Unique Key for Cache Based on User ID
        self.KEY_PREFIX = f"orders-viewset-{self.request.user.id}"
        self.list = method_decorator(cache_page(CACHE_TIMEOUT, key_prefix=self.KEY_PREFIX))(self.list)
        return super().dispatch(*args, **kwargs)

    # Processing DELETE Methods
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        delete_cache(self.KEY_PREFIX)
        return Response(status=status.HTTP_200_OK)
