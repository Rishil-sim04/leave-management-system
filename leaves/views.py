from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Leave, LeaveBalance, Holiday, CustomNotifyList
from .serializers import (
    LeaveSerializer,
    LeaveApprovalSerializer,
    LeaveBalanceSerializer,
    HolidaySerializer,
    CustomNotifyListSerializer,
)

User = get_user_model()

HIERARCHY = [
    "trainee",
    "software_engineer",
    "senior_software_engineer",
    "team_lead",
    "manager",
    "engineering_manager",
    "cto",
]


def can_approve(approver, employee):
    # Superadmin and HR can approve anyone
    if approver.is_superuser or approver.is_hr or approver.role == "hr":
        return True
    # CTO can approve engineering manager
    if approver.role == "cto" and employee.role == "engineering_manager":
        return True
    # Direct upper can approve
    if employee.reports_to and employee.reports_to == approver:
        return True
    return False


def can_apply_on_behalf(requester, target_employee):
    # HR can apply for anyone
    if requester.is_hr or requester.role == "hr":
        return True
    # Upper layer can apply for their direct subordinates
    if target_employee.reports_to and target_employee.reports_to == requester:
        return True
    # Check if requester is 2 levels above
    if (
        target_employee.reports_to
        and target_employee.reports_to.reports_to
        and target_employee.reports_to.reports_to == requester
    ):
        return True
    return False


def can_view_leave(viewer, leave):
    employee = leave.employee
    # Superadmin, HR see everything
    if viewer.is_superuser or viewer.is_hr or viewer.role == "hr":
        return True
    # Own leave
    if employee == viewer:
        return True
    # Direct upper (1 level)
    if employee.reports_to == viewer:
        return True
    # 2 levels upper
    if employee.reports_to and employee.reports_to.reports_to == viewer:
        return True
    return False



class LeaveListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser or user.is_hr or user.role == "hr":
            leaves = Leave.objects.all()
        elif user.role in ["team_lead", "manager", "engineering_manager", "cto"]:
            # Direct subordinates
            direct_ids = list(user.subordinates.values_list("id", flat=True))
            # 2 levels below
            second_level_ids = list(
                User.objects.filter(reports_to__in=direct_ids).values_list(
                    "id", flat=True
                )
            )
            all_ids = set(direct_ids + second_level_ids + [user.id])
            leaves = Leave.objects.filter(employee__in=all_ids)
        else:
            leaves = Leave.objects.filter(employee=user)

        leave_status = request.query_params.get("leave_status")
        if leave_status:
            leaves = leaves.filter(leave_status=leave_status)
        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)



    def post(self, request):
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=request.user, applied_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class LeaveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave(self, leave_id):
        return get_object_or_404(Leave, id=leave_id)

    def get(self, request, leave_id):
        leave = self.get_leave(leave_id)
        if not can_view_leave(request.user, leave):
            return Response(
                {"error": "You do not have permission to view this leave."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = LeaveSerializer(leave)
        return Response(serializer.data)


    def patch(self, request, leave_id):
        leave = self.get_leave(leave_id)
        user = request.user
        if request.data.get("approval_status") == "cancelled":
            if leave.employee != user:
                return Response(
                    {"error": "You can only cancel your own leave."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            leave.approval_status = "cancelled"
            leave.save()
            return Response({"message": "Leave Cancelled Successfully..."})
        if not can_approve(user, leave.employee):
            return Response(
                {
                    "error": "You do not have permission to approve or reject leave."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = LeaveApprovalSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(approved_by=user)
            return Response(
                {
                    "message": f"Leave {serializer.data['approval_status']} by {user.full_name}.",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ApplyOnBehalfView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, emp_id):
        employee = get_object_or_404(User, id=emp_id)
        if not can_apply_on_behalf(request.user, employee):
            return Response(
                {
                    "error": "You do not have permission to apply leave for this employee."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=employee, applied_by=request.user)
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
        holidays = Holiday.objects.all().order_by("date")
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Only HR can add holidays
        if not (request.user.is_hr or request.user.role == "hr"):
            return Response(
                {"error": "Only HR can add Holidays..."}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class LeaveBalanceManageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only HR can credit leave balance
        if not (request.user.is_hr or request.user.role == "hr"):
            return Response(
                {"error": "Only HR can manage leave balance"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = LeaveBalanceSerializer(data=request.data)
        if serializer.is_valid():
            employee_id = request.data.get("employee")
            leave_type = request.data.get("leave_type")
            balance, created = LeaveBalance.objects.get_or_create(
                employee_id=employee_id,
                leave_type=leave_type,
                defaults={"credited": 0, "used": 0},
            )
            balance.credited += float(request.data.get("credited", 0))
            balance.save()
            return Response(
                LeaveBalanceSerializer(balance).data, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





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
            CustomNotifyList, id=notify_id, employee=request.user
        )
        notify.delete()
        return Response({"message": "Person removed from Notify list..."})







 