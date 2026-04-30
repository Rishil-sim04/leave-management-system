from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from leavemanagement.utils import success_response, error_response
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="User registered successfully.",
                status_code=201
            )
        return error_response(
            message="Registration failed.",
            errors=serializer.errors
        )


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return error_response(
                message="Both old_password and new_password are required."
            )

        if not user.check_password(old_password):
            return error_response(message="Old password is incorrect.")

        if old_password == new_password:
            return error_response(
                message="New password cannot be the same as old password."
            )

        user.set_password(new_password)
        user.save()

        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return success_response(
            message="Password changed successfully. Please login again."
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return error_response(message="Refresh token is required.")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(message="Logged out successfully.")
        except Exception:
            return error_response(
                message="Invalid or already blacklisted token."
            )



class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, emp_id=None):
        user = request.user

        # If no emp_id passed, employee is updating their own profile
        if emp_id is None:
            target = user
        else:
            # Only HR or superadmin can update someone else
            if not (user.is_hr or user.role == 'hr' or user.is_superuser):
                return error_response(
                    message="You do not have permission to update other profiles.",
                    status_code=403
                )

            try:
                target = User.objects.get(id=emp_id)
            except User.DoesNotExist:
                return error_response(
                    message="Employee not found.",
                    status_code=404
                )

            # HR cannot update CTO profile
            if target.role == 'cto' and not user.is_superuser:
                return error_response(
                    message="HR cannot update CTO profile.",
                    status_code=403
                )

        # Fields an employee can update on their own profile
        allowed_own_fields = ['full_name', 'department']

        # Fields HR can additionally update on others
        allowed_hr_fields = ['full_name', 'department', 'role', 'is_hr', 'reports_to']

        if emp_id is None:
            # Employee updating themselves — restrict to safe fields only
            data = {
                key: value for key, value in request.data.items()
                if key in allowed_own_fields
            }
            if not data:
                return error_response(
                    message=f"You can only update these fields: {allowed_own_fields}"
                )
        else:
            # HR updating someone else
            data = {
                key: value for key, value in request.data.items()
                if key in allowed_hr_fields
            }
            if not data:
                return error_response(
                    message=f"You can only update these fields: {allowed_hr_fields}"
                )

        serializer = UserSerializer(target, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Profile updated successfully."
            )
        return error_response(
            message="Failed to update profile.",
            errors=serializer.errors
        )


class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # HR and superadmin see everyone
        if user.is_superuser or user.is_hr or user.role == 'hr':
            employees = User.objects.all().order_by('full_name')

        # Team lead and above see their subordinates
        elif user.role in ['team_lead', 'manager', 'engineering_manager', 'cto']:
            direct_ids = list(user.subordinates.values_list('id', flat=True))
            second_level_ids = list(
                User.objects.filter(
                    reports_to__in=direct_ids
                ).values_list('id', flat=True)
            )
            all_ids = set(direct_ids + second_level_ids + [user.id])
            employees = User.objects.filter(id__in=all_ids).order_by('full_name')

        else:
            # Regular employee can only see their own profile
            employees = User.objects.filter(id=user.id)

        # Search by name or email
        search = request.query_params.get('search')
        if search:
            employees = employees.filter(
                full_name__icontains=search
            ) | employees.filter(
                email__icontains=search
            )

        # Filter by department
        department = request.query_params.get('department')
        if department:
            employees = employees.filter(department__icontains=department)

        # Filter by role
        role = request.query_params.get('role')
        if role:
            employees = employees.filter(role=role)

        from leavemanagement.pagination import StandardPagination
        paginator = StandardPagination()
        paginated = paginator.paginate_queryset(employees, request)
        serializer = UserSerializer(paginated, many=True)

        return success_response(
            data={
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            },
            message="Employees fetched successfully."
        )
    

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response(
            data=serializer.data,
            message="Profile fetched successfully."
        )
    


     
 