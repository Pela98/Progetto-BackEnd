import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
"""
Define two roles with distinct abilities: Standard User that can log, edit, and delete their own workouts
and progress entries and can set, update, and complete their own goals. Coach with all
Standard User permissions, plus view workouts/goals across all accounts. Provide comments or
feedback on accounts’ progress.
"""
#scelte

#\scelte

#validatore licenza //DEPRECATO
def is_valid_license(license_number):
    if not license_number:
        raise ValueError("License number is required to validate")
    if len(license_number) != 10 or not license_number.isdigit():
        raise ValueError("Invalid license number")
    else:
        return True
#La data di nascita della persona più vecchia al mondo
MIN_BIRTH_DATE = datetime.date(1906, 8, 21)
#calcolatori
def calculate_bmr(height, weight, age, biogender):
    if biogender == 'M':
        return 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
    else:
        return 655.1 + (9.563 * weight) + (1.840 * height) - (4.676 * age)
def calculate_bmi(height, weight):
    return weight / (height / 100) ** 2
# un utente deve avere almeno 18 anni
def eighteen_years_ago():
    return datetime.date.today() - datetime.timedelta(days=18 * 365.25)

#il factory degli user
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        if not username:
            raise ValueError('Username is required')

        email = self.normalize_email(email)
        user = StandardUser(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.is_coach = False
        user.save(using=self._db)
        return user
    def create_superuser(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        if not username:
            raise ValueError('Username is required')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        email = self.normalize_email(email)
        user = StandardUser(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.is_coach = True
        user.save(using=self._db)
        return user
#Modello con tutte le informazioni che possono servire per calcoli che riguardano il fitness
class StandardUser(AbstractUser):
    height = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(300)], null=True)
    weight = models.DecimalField(max_digits=4, decimal_places=1,
                                 validators=[MinValueValidator(5), MaxValueValidator(700)], null=True)
    biogender = models.CharField(max_length=1, choices=[('M', 'Maschio'), ('F', 'Femmina')])
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.png')
    birth_date = models.DateField(null=True, validators=[
        MinValueValidator(MIN_BIRTH_DATE),
        MaxValueValidator(eighteen_years_ago())
        ])
    @property
    def age(self):
        if self.birth_date:
            return datetime.date.today().year - self.birth_date.year
        raise ValueError("Birth date is required to calculate age")
    is_coach = models.BooleanField(default=False)
    @property
    def bmr(self):
        if self.height and self.weight and self.age and self.biogender:
            return calculate_bmr(self.height, self.weight, self.age, self.biogender)
        return None

    @property
    def bmi(self):
        if self.height and self.weight:
            return calculate_bmi(self.height, self.weight)
        return None

    objects = CustomUserManager()
    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "standard_users"
        verbose_name = "standard_user"
        order_with_respect_to = 'username'






