
from rest_framework import serializers
from .models import Leave, LeaveBalance, Holiday, CustomNotifyList


class LeaveSerializer(serializers.ModelSerializer):
    remaining_balance = serializers.SerializerMethodField()
    class Meta:
        model = Leave
        fields = ['id', 'employee', 'applied_by', 'title', 'leave_type', 'description', 'start_date',
                    'end_date', 'approval_status', 'approved_by', 'leave_status', 'created_at', 'remaining_balance',
            ]
        read_only_fields = ['employee', 'applied_by', 'approval_status', 'approved_by', 
                            'leave_status','created_at',
            ]

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
            raise serializers.ValidationError("Start date can not be after End date.")
        return data




class LeaveApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ['approval_status']

    def validate_approval_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("You can only approve or reject leave.")
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














