from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from tests.factories import AdminUserFactory, ManagerUserFactory, CashierUserFactory


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def auth_client(user):
    """Return an authenticated APIClient for the given user."""
    client = APIClient()
    tokens = get_tokens_for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return client, tokens


def admin_client():
    user = AdminUserFactory()
    return auth_client(user)


def manager_client():
    user = ManagerUserFactory()
    return auth_client(user)


def cashier_client():
    user = CashierUserFactory()
    return auth_client(user)
