from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Leave


@receiver(post_save, sender=Leave)
def leave_post_save(sender, instance, created, **kwargs):
    from .tasks import send_leave_applied_notification, send_leave_status_notification

    # When a new leave is created, notify upper layers
    if created:
        send_leave_applied_notification.delay(instance.id)

    # When leave is approved or rejected, notify employee
    if not created and instance.approval_status in ['approved', 'rejected']:
        send_leave_status_notification.delay(instance.id)



        