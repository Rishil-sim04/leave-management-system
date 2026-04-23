from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@shared_task
def send_leave_applied_notification(leave_id):
    from .models import Leave

    try:
        leave = Leave.objects.select_related(
            'employee',
            'employee__reports_to',
            'employee__reports_to__reports_to'
        ).get(id=leave_id)

    except Leave.DoesNotExist:
        return

    employee = leave.employee
    recipients = []

    # Direct upper gets notified
    if employee.reports_to:
        recipients.append(employee.reports_to.email)

    # 2 levels upper also gets notified
    if employee.reports_to and employee.reports_to.reports_to:
        recipients.append(employee.reports_to.reports_to.email)

    # Custom notify list also gets notified
    from .models import CustomNotifyList
    custom_notifyees = CustomNotifyList.objects.filter(
        employee=employee
    ).values_list('notify_user__email', flat=True)

    recipients += list(custom_notifyees)

    if not recipients:
        return

    subject = f"Leave Application - {employee.full_name}"
    message = (
        f"{employee.full_name} has applied for {leave.leave_type} leave.\n\n"
        f"Title: {leave.title}\n"
        f"From: {leave.start_date}\n"
        f"To: {leave.end_date}\n"
        f"Reason: {leave.description}\n\n"
        f"Please review and take action."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )


@shared_task
def send_leave_status_notification(leave_id):
    from .models import Leave

    try:
        leave = Leave.objects.select_related(
            'employee',
            'approved_by'
        ).get(id=leave_id)

    except Leave.DoesNotExist:
        return

    action = leave.approval_status.capitalize()
    approved_by_name = leave.approved_by.full_name if leave.approved_by else "System"

    subject = f"Your Leave has been {action}"
    message = (
        f"Dear {leave.employee.full_name},\n\n"
        f"Your leave request titled '{leave.title}' has been {action} "
        f"by {approved_by_name}.\n\n"
        f"From: {leave.start_date}\n"
        f"To: {leave.end_date}\n\n"
        f"Thank you."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[leave.employee.email],
        fail_silently=False,
    )


@shared_task
def send_leave_reminder():
    from .models import Leave

    tomorrow = timezone.now().date() + timezone.timedelta(days=1)

    leaves = Leave.objects.select_related(
        'employee',
        'employee__reports_to'
    ).filter(
        start_date=tomorrow,
        approval_status='approved',
        leave_status='open'
    )

    for leave in leaves:
        employee = leave.employee
        recipients = [employee.email]

        if employee.reports_to:
            recipients.append(employee.reports_to.email)

        subject = f"Leave Reminder - {employee.full_name} is on leave tomorrow"
        message = (
            f"This is a reminder that {employee.full_name} has an approved leave tomorrow.\n\n"
            f"Title: {leave.title}\n"
            f"Date: {leave.start_date} to {leave.end_date}\n"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )


@shared_task
def auto_close_expired_leaves():
    from .models import Leave

    today = timezone.now().date()

    updated = Leave.objects.filter(
        end_date__lt=today,
        leave_status='open'
    ).update(leave_status='closed')

    return f"{updated} leaves closed."


@shared_task
def delete_old_cancelled_leaves():
    from .models import Leave

    one_month_ago = timezone.now() - timezone.timedelta(days=30)

    deleted, _ = Leave.objects.filter(
        approval_status='cancelled',
        created_at__lt=one_month_ago
    ).delete()

    return f"{deleted} cancelled leaves deleted."




 