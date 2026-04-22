from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('trainee', 'Trainee'),
        ('software_engineer', 'Software Engineer'),
        ('senior_software_engineer', 'Senior Software Engineer'),
        ('team_lead', 'Team Lead'),
        ('manager', 'Manager'),
        ('engineering_manager', 'Engineering Manager'),
        ('cto', 'CTO'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='trainee')
    department = models.CharField(max_length=100, blank=True)
    is_hr = models.BooleanField(default=False)
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    

 