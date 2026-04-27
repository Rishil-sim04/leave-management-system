from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from leavemanagement.utils import success_response, error_response
from leavemanagement.pagination import StandardPagination
from .models import Leave, LeaveBalance, Holiday, CustomNotifyList
from .serializers import (
    LeaveSerializer,
    LeaveApprovalSerializer,
    LeaveBalanceSerializer,
    HolidaySerializer,
    CustomNotifyListSerializer,
)
from .filters import LeaveFilter, HolidayFilter
import django_filters

User = get_user_model()


def can_approve(approver, employee):
    if approver.is_superuser or approver.is_hr or approver.role == 'hr':
        return True
    if approver.role == 'cto' and employee.role == 'engineering_manager':
        return True
    if employee.reports_to and employee.reports_to == approver:
        return True
    return False


def can_apply_on_behalf(requester, target_employee):
    if requester.is_hr or requester.role == 'hr':
        return True
    if target_employee.reports_to and target_employee.reports_to == requester:
        return True
    if (target_employee.reports_to and
            target_employee.reports_to.reports_to and
            target_employee.reports_to.reports_to == requester):
        return True
    return False


def can_view_leave(viewer, leave):
    employee = leave.employee
    if viewer.is_superuser or viewer.is_hr or viewer.role == 'hr':
        return True
    if employee == viewer:
        return True
    if employee.reports_to == viewer:
        return True
    if employee.reports_to and employee.reports_to.reports_to == viewer:
        return True
    return False


class LeaveListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_superuser or user.is_hr or user.role == 'hr':
            leaves = Leave.objects.all()

        elif user.role in ['team_lead', 'manager', 'engineering_manager', 'cto']:
            direct_ids = list(user.subordinates.values_list('id', flat=True))
            second_level_ids = list(
                User.objects.filter(
                    reports_to__in=direct_ids
                ).values_list('id', flat=True)
            )
            all_ids = set(direct_ids + second_level_ids + [user.id])
            leaves = Leave.objects.filter(employee__in=all_ids)

        else:
            leaves = Leave.objects.filter(employee=user)

        # Apply filters
        filterset = LeaveFilter(request.query_params, queryset=leaves)
        if not filterset.is_valid():
            return error_response(
                message="Invalid filters.",
                errors=filterset.errors
            )
        leaves = filterset.qs

        # Search by employee name or title
        search = request.query_params.get('search')
        if search:
            leaves = leaves.filter(
                title__icontains=search
            ) | leaves.filter(
                employee__full_name__icontains=search
            )

        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        allowed_ordering = [
            'created_at', '-created_at',
            'start_date', '-start_date',
            'end_date', '-end_date',
        ]
        if ordering in allowed_ordering:
            leaves = leaves.order_by(ordering)
        else:
            leaves = leaves.order_by('-created_at')

        # Pagination
        paginator = StandardPagination()
        paginated = paginator.paginate_queryset(leaves, request)
        serializer = LeaveSerializer(paginated, many=True)

        return success_response(
            data={
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            },
            message="Leaves fetched successfully."
        )

    def post(self, request):
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                employee=request.user,
                applied_by=request.user
            )
            return success_response(
                data=serializer.data,
                message="Leave applied successfully.",
                status_code=201
            )
        return error_response(
            message="Failed to apply leave.",
            errors=serializer.errors
        )


class LeaveDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_leave(self, leave_id):
        return get_object_or_404(Leave, id=leave_id)

    def get(self, request, leave_id):
        leave = self.get_leave(leave_id)

        if not can_view_leave(request.user, leave):
            return error_response(
                message="You do not have permission to view this leave.",
                status_code=403
            )

        serializer = LeaveSerializer(leave)
        return success_response(
            data=serializer.data,
            message="Leave fetched successfully."
        )

    def patch(self, request, leave_id):
        leave = self.get_leave(leave_id)
        user = request.user

        if request.data.get('approval_status') == 'cancelled':
            if leave.employee != user:
                return error_response(
                    message="You can only cancel your own leave.",
                    status_code=403
                )
            leave.approval_status = 'cancelled'
            leave.save()
            return success_response(message="Leave cancelled successfully.")

        if not can_approve(user, leave.employee):
            return error_response(
                message="You do not have permission to approve or reject this leave.",
                status_code=403
            )

        serializer = LeaveApprovalSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(approved_by=user)
            return success_response(
                data=serializer.data,
                message=f"Leave {serializer.validated_data['approval_status']} by {user.full_name}."
            )
        return error_response(
            message="Failed to update leave.",
            errors=serializer.errors
        )


class ApplyOnBehalfView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, emp_id):
        employee = get_object_or_404(User, id=emp_id)

        if not can_apply_on_behalf(request.user, employee):
            return error_response(
                message="You do not have permission to apply leave for this employee.",
                status_code=403
            )

        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                employee=employee,
                applied_by=request.user
            )
            return success_response(
                data=serializer.data,
                message=f"Leave applied on behalf of {employee.full_name}.",
                status_code=201
            )
        return error_response(
            message="Failed to apply leave.",
            errors=serializer.errors
        )


class LeaveBalanceView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        balances = LeaveBalance.objects.filter(employee=request.user)
        serializer = LeaveBalanceSerializer(balances, many=True)
        return success_response(
            data=serializer.data,
            message="Leave balance fetched successfully."
        )


class HolidayListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        holidays = Holiday.objects.all().order_by('date')

        filterset = HolidayFilter(request.query_params, queryset=holidays)
        if filterset.is_valid():
            holidays = filterset.qs

        paginator = StandardPagination()
        paginated = paginator.paginate_queryset(holidays, request)
        serializer = HolidaySerializer(paginated, many=True)

        return success_response(
            data={
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            },
            message="Holidays fetched successfully."
        )

    def post(self, request):
        if not (request.user.is_hr or request.user.role == 'hr'):
            return error_response(
                message="Only HR can add holidays.",
                status_code=403
            )

        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Holiday added successfully.",
                status_code=201
            )
        return error_response(
            message="Failed to add holiday.",
            errors=serializer.errors
        )


class LeaveBalanceManageView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not (request.user.is_hr or request.user.role == 'hr'):
            return error_response(
                message="Only HR can manage leave balances.",
                status_code=403
            )

        employee_id = request.data.get('employee')
        leave_type = request.data.get('leave_type')
        credited = request.data.get('credited', 0)

        if not employee_id or not leave_type:
            return error_response(
                message="employee and leave_type are required."
            )

        employee = get_object_or_404(User, id=employee_id)

        balance, created = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            defaults={'credited': 0, 'used': 0}
        )
        balance.credited += float(credited)
        balance.save()

        return success_response(
            data=LeaveBalanceSerializer(balance).data,
            message=f"Leave balance updated for {employee.full_name}."
        )


class CustomNotifyListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        notify_list = CustomNotifyList.objects.filter(employee=request.user)
        serializer = CustomNotifyListSerializer(notify_list, many=True)
        return success_response(
            data=serializer.data,
            message="Notify list fetched successfully."
        )

    def post(self, request):
        serializer = CustomNotifyListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=request.user)
            return success_response(
                data=serializer.data,
                message="Added to notify list.",
                status_code=201
            )
        return error_response(
            message="Failed to add to notify list.",
            errors=serializer.errors
        )

    def delete(self, request, notify_id):
        notify = get_object_or_404(
            CustomNotifyList,
            id=notify_id,
            employee=request.user
        )
        notify.delete()
        return success_response(message="Removed from notify list.")
