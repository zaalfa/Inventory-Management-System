from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer
from .filters import ProductFilter
from apps.users.permissions import IsAdmin, IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'price', 'stock', 'created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Admin sees all including inactive
        if self.request.user.is_admin and self.request.query_params.get('include_inactive'):
            qs = Product.objects.select_related('category')
        return qs

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        from django.db.models import F
        products = self.get_queryset().filter(stock__lte=F('min_stock'))
        serializer = ProductListSerializer(products, many=True)
        return Response({
            'count': products.count(),
            'results': serializer.data
        })

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        if not request.user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            product = Product.objects.get(pk=pk)
            product.is_active = True
            product.deleted_at = None
            product.save()
            return Response(ProductSerializer(product).data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
