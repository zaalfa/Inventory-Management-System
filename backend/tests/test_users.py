import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import AdminUserFactory, ManagerUserFactory, CashierUserFactory, UserFactory
from tests.helpers import auth_client, get_tokens_for_user


@pytest.mark.django_db
class TestUserRegistration:
    url = '/api/auth/register/'

    def test_register_cashier_success(self):
        client = APIClient()
        payload = {
            'email': 'cashier@test.com',
            'name': 'Test Cashier',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'role': 'cashier',
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='cashier@test.com').exists()

    def test_register_sets_hashed_password(self):
        client = APIClient()
        payload = {
            'email': 'user@test.com',
            'name': 'User',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        client.post(self.url, payload)
        user = User.objects.get(email='user@test.com')
        assert user.password != 'StrongPass123!'
        assert user.check_password('StrongPass123!')

    def test_register_password_mismatch(self):
        client = APIClient()
        payload = {
            'email': 'user@test.com',
            'name': 'User',
            'password': 'StrongPass123!',
            'password_confirm': 'WrongPass123!',
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self):
        UserFactory(email='exists@test.com')
        client = APIClient()
        payload = {
            'email': 'exists@test.com',
            'name': 'New User',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password_rejected(self):
        client = APIClient()
        payload = {
            'email': 'user@test.com',
            'name': 'User',
            'password': '123',
            'password_confirm': '123',
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_admin_role_requires_admin_auth(self):
        client = APIClient()
        payload = {
            'email': 'admin@test.com',
            'name': 'Admin',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'role': 'admin',
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_manager(self):
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        payload = {
            'email': 'manager@test.com',
            'name': 'Manager',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'role': 'manager',
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_201_CREATED

    def test_register_missing_email(self):
        client = APIClient()
        res = client.post(self.url, {'name': 'X', 'password': 'pass', 'password_confirm': 'pass'})
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email_format(self):
        client = APIClient()
        payload = {
            'email': 'not-an-email',
            'name': 'User',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        res = client.post(self.url, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    url = '/api/auth/login/'

    def setup_method(self):
        self.user = UserFactory(email='login@test.com')
        self.user.set_password('testpass123!')
        self.user.save()

    def test_login_success(self):
        client = APIClient()
        res = client.post(self.url, {'email': 'login@test.com', 'password': 'testpass123!'})
        assert res.status_code == status.HTTP_200_OK
        assert 'access' in res.data
        assert 'refresh' in res.data

    def test_login_wrong_password(self):
        client = APIClient()
        res = client.post(self.url, {'email': 'login@test.com', 'password': 'wrongpass'})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self):
        client = APIClient()
        res = client.post(self.url, {'email': 'ghost@test.com', 'password': 'pass'})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        client = APIClient()
        res = client.post(self.url, {'email': 'login@test.com', 'password': 'testpass123!'})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields(self):
        client = APIClient()
        res = client.post(self.url, {'email': 'login@test.com'})
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogout:
    url = '/api/auth/logout/'

    def test_logout_success(self):
        user = UserFactory()
        client, tokens = auth_client(user)
        res = client.post(self.url, {'refresh': tokens['refresh']})
        assert res.status_code == status.HTTP_200_OK

    def test_logout_blacklists_refresh_token(self):
        user = UserFactory()
        client, tokens = auth_client(user)
        client.post(self.url, {'refresh': tokens['refresh']})
        # Try to refresh with the blacklisted token
        anon = APIClient()
        res = anon.post('/api/auth/token/refresh/', {'refresh': tokens['refresh']})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_token(self):
        user = UserFactory()
        client, _ = auth_client(user)
        res = client.post(self.url, {})
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self):
        client = APIClient()
        res = client.post(self.url, {'refresh': 'sometoken'})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_invalid_token(self):
        user = UserFactory()
        client, _ = auth_client(user)
        res = client.post(self.url, {'refresh': 'totally-invalid-token'})
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMeEndpoint:
    url = '/api/auth/me/'

    def test_get_own_profile(self):
        user = UserFactory(name='John Doe', email='john@test.com', role='cashier')
        client, _ = auth_client(user)
        res = client.get(self.url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['name'] == 'John Doe'
        assert res.data['email'] == 'john@test.com'
        assert res.data['role'] == 'cashier'

    def test_unauthenticated_cannot_access(self):
        client = APIClient()
        res = client.get(self.url)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_own_name(self):
        user = UserFactory()
        client, _ = auth_client(user)
        res = client.patch(self.url, {'name': 'New Name'})
        assert res.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.name == 'New Name'

    def test_password_not_in_response(self):
        user = UserFactory()
        client, _ = auth_client(user)
        res = client.get(self.url)
        assert 'password' not in res.data


@pytest.mark.django_db
class TestChangePassword:
    url = '/api/auth/me/change-password/'

    def test_change_password_success(self):
        user = UserFactory()
        user.set_password('OldPass123!')
        user.save()
        client, _ = auth_client(user)
        res = client.put(self.url, {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!',
        })
        assert res.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('NewPass456!')

    def test_wrong_old_password(self):
        user = UserFactory()
        user.set_password('OldPass123!')
        user.save()
        client, _ = auth_client(user)
        res = client.put(self.url, {
            'old_password': 'WrongOldPass!',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'NewPass456!',
        })
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_new_password_mismatch(self):
        user = UserFactory()
        user.set_password('OldPass123!')
        user.save()
        client, _ = auth_client(user)
        res = client.put(self.url, {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password_confirm': 'DifferentPass789!',
        })
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserViewSet:
    url = '/api/auth/users/'

    def test_admin_can_list_users(self):
        UserFactory.create_batch(3)
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.get(self.url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] >= 4

    def test_non_admin_cannot_list_users(self):
        manager = ManagerUserFactory()
        client, _ = auth_client(manager)
        res = client.get(self.url)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_soft_delete_user(self):
        user = UserFactory()
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.delete(f'{self.url}{user.id}/')
        assert res.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert not user.is_active  # soft delete

    def test_admin_cannot_delete_self(self):
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.delete(f'{self.url}{admin.id}/')
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_activate_user(self):
        user = UserFactory(is_active=False)
        admin = AdminUserFactory()
        client, _ = auth_client(admin)
        res = client.post(f'{self.url}{user.id}/activate/')
        assert res.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_token_works(self):
        user = UserFactory()
        _, tokens = auth_client(user)
        client = APIClient()
        res = client.post('/api/auth/token/refresh/', {'refresh': tokens['refresh']})
        assert res.status_code == status.HTTP_200_OK
        assert 'access' in res.data

    def test_refresh_with_invalid_token(self):
        client = APIClient()
        res = client.post('/api/auth/token/refresh/', {'refresh': 'badtoken'})
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_hashes_password(self):
        user = User.objects.create_user(email='u@test.com', name='U', password='plain123')
        assert user.check_password('plain123')
        assert user.password != 'plain123'

    def test_create_superuser(self):
        user = User.objects.create_superuser(email='su@test.com', name='SU', password='pass')
        assert user.is_staff
        assert user.is_superuser
        assert user.role == 'admin'

    def test_user_role_properties(self):
        admin = AdminUserFactory()
        manager = ManagerUserFactory()
        cashier = CashierUserFactory()
        assert admin.is_admin
        assert not admin.is_manager
        assert manager.is_manager
        assert not manager.is_admin
        assert cashier.is_cashier
        assert not cashier.is_admin

    def test_create_user_without_email_raises(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email='', name='X', password='pass')

    def test_str_representation(self):
        user = UserFactory(name='Alice', role='admin')
        assert 'Alice' in str(user)
        assert 'admin' in str(user)
