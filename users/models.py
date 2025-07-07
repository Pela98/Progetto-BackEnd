from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models
# Create your models here.

class UserRoles(models.TextChoices):
    ATHLETE = 'athlete', 'Athlete'
    COACH = 'coach', 'Coach'


class Profile(AbstractUser):
    class CustomUser(AbstractUser):
        """
        Modello utente personalizzato che estende AbstractUser per includere ruoli
        e campi specifici per Coach e Athlete.
        """
        role = models.CharField(
            max_length=10,
            choices=UserRoles.choices,
            default=UserRoles.ATHLETE,
            help_text='Defines if the user is a coach or an athlete.'
        )
        age = models.IntegerField(
            null=True, blank=True,
            help_text='Age of the user.'
        )

        # Campi specifici per Coach
        gym = models.CharField(
            max_length=100, null=True, blank=True,
            help_text='The gym where the coach works.'
        )
        is_licensed = models.BooleanField(
            default=False,
            help_text='Indicates if the coach has a valid license.'
        )

        # Campi specifici per Athlete
        height = models.FloatField(
            null=True, blank=True,
            help_text='Height of the athlete in cm.'
        )
        weight = models.FloatField(
            null=True, blank=True,
            help_text='Weight of the athlete in kg.'
        )
        goal = models.TextField(
            null=True, blank=True,
            help_text='Fitness or training goal of the athlete.'
        )
        # Relazione con il Coach (un altro CustomUser con role='coach')
        coach = models.ForeignKey(
            'self',  # Riferimento allo stesso modello CustomUser
            on_delete=models.SET_NULL,
            null=True, blank=True,
            related_name='athletes',
            limit_choices_to={'role': UserRoles.COACH},  # Assicurati che solo i coach possano essere assegnati
            help_text='The coach associated with the athlete.'
        )

        objects = CustomUserManager()  # Assegna il manager personalizzato al modello

        class Meta:
            verbose_name = 'user'
            verbose_name_plural = 'users'

        def __str__(self):
            return self.username

        def is_coach(self):
            return self.role == UserRoles.COACH

        def is_athlete(self):
            return self.role == UserRoles.ATHLETE

class Athlete(Profile):
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
    coach = models.ForeignKey('Coach', on_delete = None, null=True, blank=True)


class Coach(Profile):
    isLicenced = models.BooleanField(default=False)
    gym = models.charfield(max_length=100)


class ProfileManager(UserManager):
    def create_user(self, email, username, password=<PASSWORD>, role, age, isLicenced=False, gym=None):
        if not email:
            raise ValueError('Email è un campo obbligatorio')
        if not username:
            raise ValueError('Username è un campo obbligatorio')
        if not password:
            raise ValueError('La password non può essere vuota')

