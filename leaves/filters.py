import django_filters
from .models import Leave, Holiday


class LeaveFilter(django_filters.FilterSet):

    leave_type = django_filters.CharFilter(
        field_name='leave_type',
        lookup_expr='exact'
    )

    approval_status = django_filters.CharFilter(
        field_name='approval_status',
        lookup_expr='exact'
    )

    leave_status = django_filters.CharFilter(
        field_name='leave_status',
        lookup_expr='exact'
    )

    start_date = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte'
    )

    end_date = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte'
    )

    employee_name = django_filters.CharFilter(
        field_name='employee__full_name',
        lookup_expr='icontains'
    )

    department = django_filters.CharFilter(
        field_name='employee__department',
        lookup_expr='icontains'
    )

    class Meta:
        model = Leave
        fields = [
            'leave_type',
            'approval_status',
            'leave_status',
            'start_date',
            'end_date',
            'employee_name',
            'department',
        ]


class HolidayFilter(django_filters.FilterSet):

    month = django_filters.NumberFilter(
        field_name='date',
        lookup_expr='month'
    )

    year = django_filters.NumberFilter(
        field_name='date',
        lookup_expr='year'
    )

    class Meta:
        model = Holiday
        fields = ['month', 'year']






 