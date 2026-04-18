import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal

from apps.users.models import User
from apps.products.models import Category, Product
from apps.transactions.models import Transaction
from apps.alerts.models import StockAlert

fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.unique.email())
    name = factory.LazyFunction(lambda: fake.name())
    role = 'cashier'
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'testpass123!')
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, password=password, **kwargs)


class AdminUserFactory(UserFactory):
    role = 'admin'
    is_staff = True


class ManagerUserFactory(UserFactory):
    role = 'manager'


class CashierUserFactory(UserFactory):
    role = 'cashier'


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.LazyFunction(lambda: fake.unique.word().capitalize())
    description = factory.LazyFunction(lambda: fake.sentence())


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.LazyFunction(lambda: fake.unique.catch_phrase())
    category = factory.SubFactory(CategoryFactory)
    price = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(min_value=1, max_value=1000, right_digits=2), 2))))
    stock = factory.LazyFunction(lambda: fake.random_int(min=10, max=100))
    min_stock = 5
    description = factory.LazyFunction(lambda: fake.paragraph())
    is_active = True


class LowStockProductFactory(ProductFactory):
    stock = 3
    min_stock = 5


class OutOfStockProductFactory(ProductFactory):
    stock = 0
    min_stock = 5


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    product = factory.SubFactory(ProductFactory)
    type = 'in'
    quantity = factory.LazyFunction(lambda: fake.random_int(min=1, max=20))
    stock_before = 50
    stock_after = factory.LazyAttribute(lambda o: o.stock_before + o.quantity)
    unit_price = factory.LazyFunction(lambda: Decimal('100.00'))
    user = factory.SubFactory(CashierUserFactory)
    notes = ''


class StockAlertFactory(DjangoModelFactory):
    class Meta:
        model = StockAlert

    product = factory.SubFactory(LowStockProductFactory)
    severity = StockAlert.SEVERITY_LOW
    message = factory.LazyAttribute(lambda o: f'Low stock: {o.product.name}')
    is_resolved = False
