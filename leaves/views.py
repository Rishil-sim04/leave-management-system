from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Leave, LeaveBalance, Holiday, CustomNotifyList
from .serializers import (
    LeaveSerializer,
    LeaveApprovalSerializer,
    LeaveBalanceSerializer,
    HolidaySerializer,
    CustomNotifyListSerializer,
)


def can_approve(approver, employee):
    if approver.is_hr or approver.is_staff:
        return True
    if employee.reports_to == approver:
        return True
    return False


class LeaveListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_staff or user.is_hr:
            leaves = Leave.objects.all()
        elif user.role in ['team_lead', 'manager', 'engineering_manager', 'cto']:
            subordinate_ids = user.subordinates.values_list('id', flat=True)
            leaves = Leave.objects.filter(
                employee__in=list(subordinate_ids) + [user.id]
            )
        else:
            leaves = Leave.objects.filter(employee=user)
        leave_status = request.query_params.get('leave_status')

        if leave_status:
            leaves = leaves.filter(leave_status=leave_status)

        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                employee=request.user,
                applied_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LeaveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave(self, leave_id):
        return get_object_or_404(Leave, id=leave_id)

    def get(self, request, leave_id):
        leave = self.get_leave(leave_id)
        user = request.user
        is_own = leave.employee == user
        is_subordinate = leave.employee.reports_to == user
        is_hr_or_admin = user.is_hr or user.is_staff

        if not (is_own or is_subordinate or is_hr_or_admin):
            return Response(
                {"error": "You do not have permission to view this leave."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = LeaveSerializer(leave)
        return Response(serializer.data)

    def patch(self, request, leave_id):
        leave = self.get_leave(leave_id)
        user = request.user

        if request.data.get('approval_status') == 'cancelled':
            if leave.employee != user:
                return Response(
                    {"error": "You can only cancel your own leave."},
                    status=status.HTTP_403_FORBIDDEN
                )
            leave.approval_status = 'cancelled'
            leave.save()
            return Response({"message": "Leave cancelled."})

        if not can_approve(user, leave.employee):
            return Response(
                {"error": "You do not have permission to approve or reject this leave."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LeaveApprovalSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(approved_by=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplyOnBehalfView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, emp_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if not (request.user.is_hr or request.user.is_staff):
            return Response(
                {"error": "Only HR or Admin can apply leave on behalf of an employee."},
                status=status.HTTP_403_FORBIDDEN
            )
        employee = get_object_or_404(User, id=emp_id)
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                employee=employee,
                applied_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LeaveBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        balances = LeaveBalance.objects.filter(employee=request.user)
        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response(serializer.data)





class HolidayListView(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        holidays = Holiday.objects.all().order_by('date')
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)




class CustomNotifyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notify_list = CustomNotifyList.objects.filter(employee=request.user)
        serializer = CustomNotifyListSerializer(notify_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomNotifyListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, notify_id):
        notify = get_object_or_404(
            CustomNotifyList,
            id=notify_id,
            employee=request.user
        )
        notify.delete()
        return Response({"message": "Removed from notify list."})
    




 


 