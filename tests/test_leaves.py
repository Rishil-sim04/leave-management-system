import pytest
from django.contrib.auth import get_user_model
from leaves.models import Leave, LeaveBalance, Holiday

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_hierarchy(create_user):
    manager = create_user(
        email='manager@example.com',
        full_name='Manager Person',
        role='manager',
        department='Engineering'
    )
    employee = create_user(
        email='emp@example.com',
        full_name='Emp Person',
        role='trainee',
        department='Engineering',
        reports_to=manager
    )
    hr = create_user(
        email='hr@example.com',
        full_name='HR Person',
        role='hr',
        is_hr=True
    )
    return {'manager': manager, 'employee': employee, 'hr': hr}


@pytest.fixture
def leave_payload():
    return {
        'title': 'Test Leave',
        'leave_type': 'paid',
        'description': 'Going on leave',
        'start_date': '2025-08-01',
        'end_date': '2025-08-03',
    }


class TestApplyLeave:

    def test_employee_can_apply_leave(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        res = client.post('/leaves/', leave_payload, format='json')
        assert res.status_code == 201
        assert res.data['success'] is True

    def test_apply_leave_start_after_end(self, auth_client, setup_hierarchy):
        client = auth_client(setup_hierarchy['employee'])
        payload = {
            'title': 'Bad Leave',
            'leave_type': 'paid',
            'description': 'Wrong dates',
            'start_date': '2025-08-05',
            'end_date': '2025-08-01',
        }
        res = client.post('/leaves/', payload, format='json')
        assert res.status_code == 400

    def test_apply_leave_missing_fields(self, auth_client, setup_hierarchy):
        client = auth_client(setup_hierarchy['employee'])
        res = client.post('/leaves/', {'title': 'Incomplete'}, format='json')
        assert res.status_code == 400

    def test_unauthenticated_cannot_apply(self, api_client, leave_payload):
        res = api_client.post('/leaves/', leave_payload, format='json')
        assert res.status_code == 401


class TestViewLeaves:

    def test_employee_sees_own_leaves(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        client.post('/leaves/', leave_payload, format='json')
        res = client.get('/leaves/')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 1

    def test_manager_sees_subordinate_leaves(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        emp_client.post('/leaves/', leave_payload, format='json')

        manager_client = auth_client(setup_hierarchy['manager'])
        res = manager_client.get('/leaves/')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 1

    def test_hr_sees_all_leaves(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        emp_client.post('/leaves/', leave_payload, format='json')

        hr_client = auth_client(setup_hierarchy['hr'])
        res = hr_client.get('/leaves/')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 1

    def test_filter_by_leave_type(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        client.post('/leaves/', leave_payload, format='json')
        res = client.get('/leaves/?leave_type=paid')
        assert res.status_code == 200
        for leave in res.data['data']['results']:
            assert leave['leave_type'] == 'paid'

    def test_filter_by_approval_status(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        client.post('/leaves/', leave_payload, format='json')
        res = client.get('/leaves/?approval_status=pending')
        assert res.status_code == 200
        for leave in res.data['data']['results']:
            assert leave['approval_status'] == 'pending'

    def test_search_by_title(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        client.post('/leaves/', leave_payload, format='json')
        res = client.get('/leaves/?search=Test Leave')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 1

    def test_pagination_page_size(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        for _ in range(3):
            client.post('/leaves/', leave_payload, format='json')
        res = client.get('/leaves/?page_size=2')
        assert res.status_code == 200
        assert len(res.data['data']['results']) <= 2


class TestLeaveDetail:

    def test_employee_can_view_own_leave(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        create_res = client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']
        res = client.get(f'/leaves/{leave_id}/')
        assert res.status_code == 200
        assert res.data['data']['id'] == leave_id

    def test_response_contains_employee_details(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        create_res = client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']
        res = client.get(f'/leaves/{leave_id}/')
        assert 'employee_detail' in res.data['data']
        assert 'full_name' in res.data['data']['employee_detail']
        assert 'email' in res.data['data']['employee_detail']

    def test_other_employee_cannot_view_leave(self, create_user, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        create_res = client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']

        other = create_user(email='other@example.com', full_name='Other', role='trainee')
        other_client = auth_client(other)
        res = other_client.get(f'/leaves/{leave_id}/')
        assert res.status_code == 403

    def test_manager_can_view_subordinate_leave(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        create_res = emp_client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']

        manager_client = auth_client(setup_hierarchy['manager'])
        res = manager_client.get(f'/leaves/{leave_id}/')
        assert res.status_code == 200


class TestLeaveApproval:

    def test_manager_can_approve_leave(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        create_res = emp_client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']

        manager_client = auth_client(setup_hierarchy['manager'])
        res = manager_client.patch(f'/leaves/{leave_id}/', {
            'approval_status': 'approved'
        }, format='json')
        assert res.status_code == 200
        assert res.data['success'] is True

    def test_manager_can_reject_leave(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        create_res = emp_client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']

        manager_client = auth_client(setup_hierarchy['manager'])
        res = manager_client.patch(f'/leaves/{leave_id}/', {
            'approval_status': 'rejected'
        }, format='json')
        assert res.status_code == 200

    def test_approved_by_shows_in_response(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        create_res = emp_client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']

        manager_client = auth_client(setup_hierarchy['manager'])
        manager_client.patch(f'/leaves/{leave_id}/', {
            'approval_status': 'approved'
        }, format='json')

        res = emp_client.get(f'/leaves/{leave_id}/')
        assert res.data['data']['approved_by_detail']['full_name'] == 'Manager Person'

    def test_employee_cannot_approve_own_leave(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        create_res = client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']
        res = client.patch(f'/leaves/{leave_id}/', {
            'approval_status': 'approved'
        }, format='json')
        assert res.status_code == 403

    def test_hr_can_approve_any_leave(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        create_res = emp_client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']

        hr_client = auth_client(setup_hierarchy['hr'])
        res = hr_client.patch(f'/leaves/{leave_id}/', {
            'approval_status': 'approved'
        }, format='json')
        assert res.status_code == 200

    def test_employee_can_cancel_own_leave(self, auth_client, setup_hierarchy, leave_payload):
        client = auth_client(setup_hierarchy['employee'])
        create_res = client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']
        res = client.patch(f'/leaves/{leave_id}/', {
            'approval_status': 'cancelled'
        }, format='json')
        assert res.status_code == 200

    def test_cannot_set_invalid_status(self, auth_client, setup_hierarchy, leave_payload):
        emp_client = auth_client(setup_hierarchy['employee'])
        create_res = emp_client.post('/leaves/', leave_payload, format='json')
        leave_id = create_res.data['data']['id']

        manager_client = auth_client(setup_hierarchy['manager'])
        res = manager_client.patch(f'/leaves/{leave_id}/', {
            'approval_status': 'something_random'
        }, format='json')
        assert res.status_code == 400


class TestApplyOnBehalf:

    def test_hr_can_apply_on_behalf(self, auth_client, setup_hierarchy, leave_payload):
        hr_client = auth_client(setup_hierarchy['hr'])
        emp_id = setup_hierarchy['employee'].id
        res = hr_client.post(f'/leaves/behalf/{emp_id}/', leave_payload, format='json')
        assert res.status_code == 201
        assert res.data['data']['employee'] == emp_id

    def test_manager_can_apply_for_subordinate(self, auth_client, setup_hierarchy, leave_payload):
        manager_client = auth_client(setup_hierarchy['manager'])
        emp_id = setup_hierarchy['employee'].id
        res = manager_client.post(f'/leaves/behalf/{emp_id}/', leave_payload, format='json')
        assert res.status_code == 201

    def test_random_employee_cannot_apply_on_behalf(self, create_user, auth_client, setup_hierarchy, leave_payload):
        other = create_user(email='other@example.com', full_name='Other', role='trainee')
        client = auth_client(other)
        emp_id = setup_hierarchy['employee'].id
        res = client.post(f'/leaves/behalf/{emp_id}/', leave_payload, format='json')
        assert res.status_code == 403


class TestLeaveBalance:

    def test_view_own_balance(self, auth_client, setup_hierarchy):
        LeaveBalance.objects.create(
            employee=setup_hierarchy['employee'],
            leave_type='paid',
            credited=10,
            used=2
        )
        client = auth_client(setup_hierarchy['employee'])
        res = client.get('/leaves/balance/')
        assert res.status_code == 200
        assert len(res.data['data']) >= 1
        assert res.data['data'][0]['remaining'] == 8

    def test_hr_can_credit_balance(self, auth_client, setup_hierarchy):
        hr_client = auth_client(setup_hierarchy['hr'])
        res = hr_client.post('/leaves/balance/manage/', {
            'employee': setup_hierarchy['employee'].id,
            'leave_type': 'paid',
            'credited': 5
        }, format='json')
        assert res.status_code == 200
        assert res.data['success'] is True

    def test_employee_cannot_credit_balance(self, auth_client, setup_hierarchy):
        client = auth_client(setup_hierarchy['employee'])
        res = client.post('/leaves/balance/manage/', {
            'employee': setup_hierarchy['employee'].id,
            'leave_type': 'paid',
            'credited': 5
        }, format='json')
        assert res.status_code == 403


class TestHolidays:

    def test_anyone_can_view_holidays(self, auth_client, setup_hierarchy):
        Holiday.objects.create(date='2025-08-15', day='Friday', title='Independence Day')
        client = auth_client(setup_hierarchy['employee'])
        res = client.get('/leaves/holidays/')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 1

    def test_hr_can_add_holiday(self, auth_client, setup_hierarchy):
        hr_client = auth_client(setup_hierarchy['hr'])
        res = hr_client.post('/leaves/holidays/', {
            'date': '2025-10-02',
            'day': 'Thursday',
            'title': 'Gandhi Jayanti'
        }, format='json')
        assert res.status_code == 201

    def test_employee_cannot_add_holiday(self, auth_client, setup_hierarchy):
        client = auth_client(setup_hierarchy['employee'])
        res = client.post('/leaves/holidays/', {
            'date': '2025-10-02',
            'day': 'Thursday',
            'title': 'Gandhi Jayanti'
        }, format='json')
        assert res.status_code == 403

    def test_filter_holidays_by_month(self, auth_client, setup_hierarchy):
        Holiday.objects.create(date='2025-08-15', day='Friday', title='Independence Day')
        client = auth_client(setup_hierarchy['employee'])
        res = client.get('/leaves/holidays/?month=8')
        assert res.status_code == 200
        assert res.data['data']['count'] >= 1


class TestNotifyList:

    def test_add_to_notify_list(self, auth_client, setup_hierarchy):
        client = auth_client(setup_hierarchy['employee'])
        res = client.post('/leaves/notify/', {
            'notify_user': setup_hierarchy['manager'].id
        }, format='json')
        assert res.status_code == 201

    def test_view_notify_list(self, auth_client, setup_hierarchy):
        client = auth_client(setup_hierarchy['employee'])
        client.post('/leaves/notify/', {
            'notify_user': setup_hierarchy['manager'].id
        }, format='json')
        res = client.get('/leaves/notify/')
        assert res.status_code == 200
        assert len(res.data['data']) >= 1

    def test_remove_from_notify_list(self, auth_client, setup_hierarchy):
        client = auth_client(setup_hierarchy['employee'])
        add_res = client.post('/leaves/notify/', {
            'notify_user': setup_hierarchy['manager'].id
        }, format='json')
        notify_id = add_res.data['data']['id']
        res = client.delete(f'/leaves/notify/{notify_id}/')
        assert res.status_code == 200









        