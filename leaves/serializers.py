from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Leave, LeaveBalance, Holiday, CustomNotifyList

User = get_user_model()


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'role', 'department']




class LeaveSerializer(serializers.ModelSerializer):

    remaining_balance = serializers.SerializerMethodField()
    employee_detail = BasicUserSerializer(source='employee', read_only=True)
    applied_by_detail = BasicUserSerializer(source='applied_by', read_only=True)
    approved_by_detail = BasicUserSerializer(source='approved_by', read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id', 'employee', 'employee_detail', 'applied_by', 'applied_by_detail', 'title', 'leave_type', 'description',
            'start_date', 'end_date', 'approval_status', 'approved_by', 'approved_by_detail', 'leave_status', 'created_at', 'remaining_balance',
        ]
        read_only_fields = [ 'employee', 'applied_by', 'approval_status', 'approved_by', 'leave_status', 'created_at',]

    def get_remaining_balance(self, obj):
        try:
            balance = LeaveBalance.objects.get(
                employee=obj.employee,
                leave_type=obj.leave_type
            )
            return balance.remaining
        except LeaveBalance.DoesNotExist:
            return None
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be after end date.")
        return data





class LeaveApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ['approval_status']
    def validate_approval_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("You can only approve or reject a leave.")
        return value




class LeaveBalanceSerializer(serializers.ModelSerializer):
    remaining = serializers.ReadOnlyField()
    class Meta:
        model = LeaveBalance
        fields = ['id', 'employee', 'leave_type', 'credited', 'used', 'remaining']
        read_only_fields = ['employee']




class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'date', 'day', 'title']




class CustomNotifyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomNotifyList
        fields = ['id', 'employee', 'notify_user']
        read_only_fields = ['employee']




 
 
 