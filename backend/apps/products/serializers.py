from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'sku',
            'price', 'stock', 'min_stock', 'description',
            'image', 'is_active', 'stock_status', 'is_low_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sku', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock cannot be negative.')
        return value

    def validate_min_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Minimum stock cannot be negative.')
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category_name', 'sku', 'price', 'stock', 'stock_status', 'image']
