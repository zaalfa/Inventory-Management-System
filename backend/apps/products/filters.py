import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    category = django_filters.NumberFilter(field_name='category__id')

    class Meta:
        model = Product
        fields = ['category', 'is_active', 'min_price', 'max_price', 'low_stock']

    def filter_low_stock(self, queryset, name, value):
        if value:
            from django.db.models import F
            return queryset.filter(stock__lte=F('min_stock'))
        return queryset
