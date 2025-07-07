from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
class Athlete(AbstractUser):
    age = models.PositiveIntegerField()
    #Scelte
    GOALS = (
    ('Weight Loss', 'Weight Loss'),
    ('Muscle Gain', 'Muscle Gain'),
    ('Stress Relief', 'Stress Relief'),
    ('Physical Strength', 'Physical Strength'),
    ('Mind and Body', 'Mind and Body'),
    ('Healthy Lifestyle', 'Healthy Lifestyle'),
    ('Other', 'Other')
    )
    #\Scelte
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()
    goal = models.CharField(max_length=100, choices=GOALS, default='Healthy Lifestyle')
    role=models.CharField(max_length=100, default='Athlete')
    def __str__(self):
        return self.username

class Coach(AbstractUser):
    role = models.CharField(max_length=100, default='Coach')
    gyms = models.listField()
    def __str__(self):
        return self.username

