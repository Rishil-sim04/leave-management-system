import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(**kwargs):
        password = kwargs.pop('password', 'testpass123')
        user = User.objects.create(**kwargs)
        user.set_password(password)
        user.save()
        return user
    return make_user


@pytest.fixture
def get_tokens(api_client):
    def fetch_tokens(email, password):
        res = api_client.post('/auth/login/', {
            'email': email,
            'password': password
        }, format='json')
        return res.data
    return fetch_tokens


@pytest.fixture
def auth_client(api_client):
    def make_auth_client(user, password='testpass123'):
        res = api_client.post('/auth/login/', {
            'email': user.email,
            'password': password
        }, format='json')
        access = res.data['access']
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        return api_client
    return make_auth_client