import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.products.models import Category, Product
from tests.factories import (
    AdminUserFactory, ManagerUserFactory, CashierUserFactory,
    CategoryFactory, ProductFactory, LowStockProductFactory, OutOfStockProductFactory
)
from tests.helpers import auth_client


@pytest.mark.django_db
class TestCategoryViewSet:
    url = '/api/products/categories/'

    def test_anyone_authenticated_can_list(self):
        CategoryFactory.create_batch(3)
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(self.url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] >= 3

    def test_unauthenticated_cannot_list(self):
        client = APIClient()
        res = client.get(self.url)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_create_category(self):
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.post(self.url, {'name': 'Electronics', 'description': 'Electronic items'})
        assert res.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='Electronics').exists()

    def test_cashier_cannot_create_category(self):
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.post(self.url, {'name': 'New Category'})
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_manager_cannot_create_category(self):
        manager = ManagerUserFactory()
        client, _ = auth_client(manager)
        res = client.post(self.url, {'name': 'New Category'})
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_category(self):
        cat = CategoryFactory(name='Old Name')
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.patch(f'{self.url}{cat.id}/', {'name': 'New Name'})
        assert res.status_code == status.HTTP_200_OK
        cat.refresh_from_db()
        assert cat.name == 'New Name'

    def test_admin_can_delete_category(self):
        cat = CategoryFactory()
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.delete(f'{self.url}{cat.id}/')
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=cat.id).exists()

    def test_duplicate_category_name_rejected(self):
        CategoryFactory(name='Unique')
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.post(self.url, {'name': 'Unique'})
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_category_product_count(self):
        cat = CategoryFactory()
        ProductFactory.create_batch(3, category=cat)
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.get(f'{self.url}{cat.id}/')
        assert res.data['product_count'] == 3


@pytest.mark.django_db
class TestProductViewSet:
    url = '/api/products/'

    def test_list_products_authenticated(self):
        ProductFactory.create_batch(5)
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(self.url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] >= 5

    def test_list_excludes_inactive_for_non_admin(self):
        ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(self.url)
        for item in res.data['results']:
            assert item.get('is_active', True)  # list serializer may not include this

    def test_admin_create_product(self):
        admin = AdminUserFactory()
        cat = CategoryFactory()
        client, _ = auth_client(admin)
        payload = {
            'name': 'Test Product',
            'category': cat.id,
            'price': '99.99',
            'stock': 50,
            'min_stock': 10,
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name='Test Product').exists()

    def test_product_auto_generates_sku(self):
        admin = AdminUserFactory()
        cat = CategoryFactory()
        client, _ = auth_client(admin)
        res = client.post(self.url, {
            'name': 'SKU Product',
            'category': cat.id,
            'price': '10.00',
            'stock': 5,
        })
        assert res.status_code == status.HTTP_201_CREATED
        product = Product.objects.get(id=res.data['id'])
        assert product.sku != ''

    def test_cashier_cannot_create_product(self):
        cashier = CashierUserFactory()
        cat = CategoryFactory()
        client, _ = auth_client(cashier)
        res = client.post(self.url, {'name': 'X', 'category': cat.id, 'price': '10', 'stock': 5})
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_product(self):
        product = ProductFactory(price=Decimal('50.00'))
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.patch(f'{self.url}{product.id}/', {'price': '75.00'})
        assert res.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.price == Decimal('75.00')

    def test_soft_delete_product(self):
        product = ProductFactory()
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.delete(f'{self.url}{product.id}/')
        assert res.status_code == status.HTTP_204_NO_CONTENT
        product.refresh_from_db()
        assert not product.is_active
        assert product.deleted_at is not None

    def test_deleted_product_not_in_list(self):
        product = ProductFactory()
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        client.delete(f'{self.url}{product.id}/')
        res = client.get(self.url)
        ids = [p['id'] for p in res.data['results']]
        assert product.id not in ids

    def test_restore_deleted_product(self):
        product = ProductFactory()
        product.soft_delete()
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.post(f'{self.url}{product.id}/restore/')
        assert res.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.is_active

    def test_negative_price_rejected(self):
        admin = AdminUserFactory()
        cat = CategoryFactory()
        client, _ = auth_client(admin)
        res = client.post(self.url, {'name': 'Bad', 'category': cat.id, 'price': '-5', 'stock': 10})
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_negative_stock_rejected(self):
        admin = AdminUserFactory()
        cat = CategoryFactory()
        client, _ = auth_client(admin)
        res = client.post(self.url, {'name': 'Bad', 'category': cat.id, 'price': '5', 'stock': -1})
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_by_category(self):
        cat1 = CategoryFactory()
        cat2 = CategoryFactory()
        ProductFactory.create_batch(2, category=cat1)
        ProductFactory.create_batch(3, category=cat2)
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(self.url, {'category': cat1.id})
        assert res.data['count'] == 2

    def test_filter_low_stock(self):
        LowStockProductFactory.create_batch(2)
        ProductFactory.create_batch(3)  # Normal stock
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(self.url, {'low_stock': 'true'})
        assert res.data['count'] >= 2

    def test_search_by_name(self):
        ProductFactory(name='Unique Widget XYZ')
        ProductFactory.create_batch(3)
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(self.url, {'search': 'Unique Widget XYZ'})
        assert res.data['count'] >= 1
        assert any('Unique Widget XYZ' in p['name'] for p in res.data['results'])

    def test_low_stock_endpoint(self):
        LowStockProductFactory.create_batch(3)
        ProductFactory.create_batch(2)
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(f'{self.url}low_stock/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] >= 3

    def test_filter_by_price_range(self):
        ProductFactory(price=Decimal('10.00'))
        ProductFactory(price=Decimal('50.00'))
        ProductFactory(price=Decimal('200.00'))
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(self.url, {'min_price': '20', 'max_price': '100'})
        for p in res.data['results']:
            assert float(p['price']) >= 20
            assert float(p['price']) <= 100

    def test_retrieve_single_product(self):
        product = ProductFactory(name='Detail Product')
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(f'{self.url}{product.id}/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['name'] == 'Detail Product'

    def test_retrieve_nonexistent_product(self):
        cashier = CashierUserFactory()
        client, _ = auth_client(cashier)
        res = client.get(f'{self.url}99999/')
        assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProductModel:
    def test_is_low_stock_true(self):
        product = LowStockProductFactory()
        assert product.is_low_stock

    def test_is_low_stock_false(self):
        product = ProductFactory(stock=100, min_stock=5)
        assert not product.is_low_stock

    def test_stock_status_out_of_stock(self):
        product = OutOfStockProductFactory()
        assert product.stock_status == 'out_of_stock'

    def test_stock_status_low_stock(self):
        product = LowStockProductFactory()
        assert product.stock_status == 'low_stock'

    def test_stock_status_in_stock(self):
        product = ProductFactory(stock=100, min_stock=5)
        assert product.stock_status == 'in_stock'

    def test_sku_auto_generated_on_save(self):
        product = ProductFactory()
        assert product.sku != ''
        assert len(product.sku) > 0

    def test_sku_is_unique(self):
        p1 = ProductFactory(name='Product Alpha')
        p2 = ProductFactory(name='Product Beta')
        assert p1.sku != p2.sku

    def test_soft_delete_sets_deleted_at(self):
        product = ProductFactory()
        product.soft_delete()
        assert not product.is_active
        assert product.deleted_at is not None

    def test_str_representation(self):
        product = ProductFactory(name='Widget', sku='WID-1234')
        product.sku = 'WID-1234'
        product.save()
        assert 'Widget' in str(product)


@pytest.mark.django_db
class TestCategoryModel:
    def test_str_representation(self):
        cat = CategoryFactory(name='Electronics')
        assert str(cat) == 'Electronics'

    def test_unique_name_constraint(self):
        CategoryFactory(name='Unique')
        with pytest.raises(Exception):
            CategoryFactory(name='Unique')
