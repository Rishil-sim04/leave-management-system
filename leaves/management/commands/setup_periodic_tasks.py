from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):

    help = 'Setup periodic celery beat tasks'

    def handle(self, *args, **kwargs):

        # Every day at 8 AM
        daily_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='8',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        # Every 1st of the month at midnight
        monthly_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_week='*',
            day_of_month='1',
            month_of_year='*',
        )

        PeriodicTask.objects.get_or_create(
            name='Send Leave Reminders Daily',
            defaults={
                'crontab': daily_schedule,
                'task': 'leaves.tasks.send_leave_reminder',
                'args': json.dumps([]),
            }
        )

        PeriodicTask.objects.get_or_create(
            name='Auto Close Expired Leaves Daily',
            defaults={
                'crontab': daily_schedule,
                'task': 'leaves.tasks.auto_close_expired_leaves',
                'args': json.dumps([]),
            }
        )

        PeriodicTask.objects.get_or_create(
            name='Delete Old Cancelled Leaves Monthly',
            defaults={
                'crontab': monthly_schedule,
                'task': 'leaves.tasks.delete_old_cancelled_leaves',
                'args': json.dumps([]),
            }
        )

        self.stdout.write(self.style.SUCCESS('Periodic tasks created successfully.'))


        