from django.db import models
from django.conf import settings


class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [('paid', 'Paid'), ('unpaid', 'Unpaid'),
                            ('sick', 'Sick'), ('casual', 'Casual'),
                    ]
    APPROVAL_STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'),
                                ('rejected', 'Rejected'), ('cancelled', 'Cancelled'),
                        ]
    LEAVE_STATUS_CHOICES = [ ('open', 'Open'), ('closed', 'Closed'),]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applied_on_behalf'
    )
    title = models.CharField(max_length=200)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    leave_status = models.CharField(
        max_length=10,
        choices=LEAVE_STATUS_CHOICES,
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.title} ({self.approval_status})"
    


 

class LeaveBalance(models.Model):
    LEAVE_TYPE_CHOICES = [ ('paid', 'Paid'), ('unpaid', 'Unpaid'),
                            ('sick', 'Sick'), ('casual', 'Casual'),
                    ]
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    credited = models.FloatField(default=0)
    used = models.FloatField(default=0)


    @property
    def remaining(self):
        return self.credited - self.used

    class Meta:
        unique_together = ('employee', 'leave_type')

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} - Remaining: {self.remaining}"
    




class Holiday(models.Model):
    date = models.DateField(unique=True)
    day = models.CharField(max_length=20)
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} on {self.date}"
    








class CustomNotifyList(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notify_list_owner'
    )
    notify_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notify_list_member'
    )

    class Meta:
        unique_together = ('employee', 'notify_user')

    def __str__(self):
        return f"{self.employee.username} notifies {self.notify_user.username}"


 



 


