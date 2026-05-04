import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestRegister:

    def test_register_success(self, api_client):
        payload = {
            'email': 'rishil@example.com',
            'full_name': 'Rishil Kathiriya',
            'password': 'testpass123',
            'role': 'trainee',
            'department': 'Engineering',
        }
        res = api_client.post('/auth/register/', payload, format='json')
        assert res.status_code == 201
        assert res.data['success'] is True
        assert 'registered' in res.data['message'].lower()

    def test_register_duplicate_email(self, api_client, create_user):
        create_user(
            email='rishil@example.com',
            full_name='Rishil',
            role='trainee'
        )
        payload = {
            'email': 'rishil@example.com',
            'full_name': 'Another Person',
            'password': 'testpass123',
            'role': 'trainee',
        }
        res = api_client.post('/auth/register/', payload, format='json')
        assert res.status_code == 400
        assert res.data['success'] is False

    def test_register_missing_email(self, api_client):
        payload = {
            'full_name': 'Rishil',
            'password': 'testpass123',
            'role': 'trainee',
        }
        res = api_client.post('/auth/register/', payload, format='json')
        assert res.status_code == 400

    def test_register_missing_password(self, api_client):
        payload = {
            'email': 'rishil@example.com',
            'full_name': 'Rishil',
            'role': 'trainee',
        }
        res = api_client.post('/auth/register/', payload, format='json')
        assert res.status_code == 400


class TestLogin:

    def test_login_success(self, api_client, create_user):
        create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        res = api_client.post('/auth/login/', {
            'email': 'rishil@example.com',
            'password': 'testpass123'
        }, format='json')
        assert res.status_code == 200
        assert 'access' in res.data
        assert 'refresh' in res.data

    def test_login_wrong_password(self, api_client, create_user):
        create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        res = api_client.post('/auth/login/', {
            'email': 'rishil@example.com',
            'password': 'wrongpass'
        }, format='json')
        assert res.status_code == 401

    def test_login_wrong_email(self, api_client):
        res = api_client.post('/auth/login/', {
            'email': 'nobody@example.com',
            'password': 'testpass123'
        }, format='json')
        assert res.status_code == 401

    def test_login_missing_fields(self, api_client):
        res = api_client.post('/auth/login/', {}, format='json')
        assert res.status_code == 400


class TestLogout:

    def test_logout_success(self, api_client, create_user, get_tokens):
        create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        tokens = get_tokens('rishil@example.com', 'testpass123')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])
        res = api_client.post('/auth/logout/', {
            'refresh': tokens['refresh']
        }, format='json')
        assert res.status_code == 200
        assert res.data['success'] is True

    def test_logout_without_refresh_token(self, api_client, create_user, auth_client):
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.post('/auth/logout/', {}, format='json')
        assert res.status_code == 400

    def test_logout_without_auth(self, api_client):
        res = api_client.post('/auth/logout/', {'refresh': 'sometoken'}, format='json')
        assert res.status_code == 401


class TestPasswordChange:

    def test_change_password_success(self, create_user, auth_client):
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.post('/auth/password-change/', {
            'old_password': 'testpass123',
            'new_password': 'newpass456'
        }, format='json')
        assert res.status_code == 200
        assert res.data['success'] is True

    def test_change_password_wrong_old(self, create_user, auth_client):
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.post('/auth/password-change/', {
            'old_password': 'wrongpass',
            'new_password': 'newpass456'
        }, format='json')
        assert res.status_code == 400

    def test_change_password_same_as_old(self, create_user, auth_client):
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.post('/auth/password-change/', {
            'old_password': 'testpass123',
            'new_password': 'testpass123'
        }, format='json')
        assert res.status_code == 400

    def test_change_password_missing_fields(self, create_user, auth_client):
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.post('/auth/password-change/', {
            'old_password': 'testpass123'
        }, format='json')
        assert res.status_code == 400



class TestProfile:

    def test_view_profile_success(self, create_user, auth_client):
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.get('/auth/show-profile/')
        assert res.status_code == 200
        assert res.data['data']['email'] == 'rishil@example.com'

    def test_view_profile_unauthenticated(self, api_client):
        res = api_client.get('/auth/show-profile/')
        assert res.status_code == 401

    def test_update_own_profile_success(self, create_user, auth_client):
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.patch('/auth/profile/', {
            'full_name': 'Rishil Updated'
        }, format='json')
        assert res.status_code == 200
        assert res.data['success'] is True

    def test_update_profile_restricted_fields(self, create_user, auth_client):
        # Employee should not be able to change their own role
        user = create_user(email='rishil@example.com', full_name='Rishil', role='trainee')
        client = auth_client(user)
        res = client.patch('/auth/profile/', {
            'role': 'cto'
        }, format='json')
        # Request goes through but role change is silently ignored
        user.refresh_from_db()
        assert user.role == 'trainee'

    def test_hr_update_employee_profile(self, create_user, auth_client):
        hr = create_user(email='hr@example.com', full_name='HR Person', role='hr', is_hr=True)
        emp = create_user(email='emp@example.com', full_name='Employee', role='trainee')
        client = auth_client(hr)
        res = client.patch(f'/auth/profile/{emp.id}/', {
            'role': 'software_engineer'
        }, format='json')
        assert res.status_code == 200
        emp.refresh_from_db()
        assert emp.role == 'software_engineer'

    def test_hr_cannot_update_cto_profile(self, create_user, auth_client):
        hr = create_user(email='hr@example.com', full_name='HR Person', role='hr', is_hr=True)
        cto = create_user(email='cto@example.com', full_name='CTO Person', role='cto')
        client = auth_client(hr)
        res = client.patch(f'/auth/profile/{cto.id}/', {
            'full_name': 'New Name'
        }, format='json')
        assert res.status_code == 403

    def test_employee_cannot_update_others_profile(self, create_user, auth_client):
        emp1 = create_user(email='emp1@example.com', full_name='Emp One', role='trainee')
        emp2 = create_user(email='emp2@example.com', full_name='Emp Two', role='trainee')
        client = auth_client(emp1)
        res = client.patch(f'/auth/profile/{emp2.id}/', {
            'full_name': 'Hacked Name'
        }, format='json')
        assert res.status_code == 403


class TestEmployeeList:

    def test_hr_sees_all_employees(self, create_user, auth_client):
        hr = create_user(email='hr@example.com', full_name='HR', role='hr', is_hr=True)
        create_user(email='e1@example.com', full_name='Emp One', role='trainee')
        create_user(email='e2@example.com', full_name='Emp Two', role='trainee')
        client = auth_client(hr)
        res = client.get('/auth/employees/')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 3

    def test_employee_sees_only_themselves(self, create_user, auth_client):
        emp = create_user(email='emp@example.com', full_name='Emp', role='trainee')
        create_user(email='other@example.com', full_name='Other', role='trainee')
        client = auth_client(emp)
        res = client.get('/auth/employees/')
        assert res.status_code == 200
        assert res.data['data']['count'] == 1

    def test_search_employee_by_name(self, create_user, auth_client):
        hr = create_user(email='hr@example.com', full_name='HR', role='hr', is_hr=True)
        create_user(email='rishil@example.com', full_name='Rishil Kathiriya', role='trainee')
        client = auth_client(hr)
        res = client.get('/auth/employees/?search=rishil')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 1

    def test_filter_by_role(self, create_user, auth_client):
        hr = create_user(email='hr@example.com', full_name='HR', role='hr', is_hr=True)
        create_user(email='tl@example.com', full_name='Team Lead', role='team_lead')
        client = auth_client(hr)
        res = client.get('/auth/employees/?role=team_lead')
        assert res.status_code == 200
        for emp in res.data['data']['results']:
            assert emp['role'] == 'team_lead'





    


 