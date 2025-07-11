#fitness/models.py

import datetime
from enum import nonmember

from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models

from django_project.settings import AUTH_USER_MODEL


#scelte

#\scelte

def calculate_bmi(height, weight):
    return weight / (height / 100) ** 2

class Goal(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    target_weight = models.DecimalField(default=None, null=True, max_digits=4, decimal_places=1, validators=[MinValueValidator(5), MaxValueValidator(700)])
    @property
    def target_bmi(self):
        if self.target_weight:
            return calculate_bmi(self.user.height, self.target_weight)
        return None
    # l'istanza di goal è riferita ad un user
    user= models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals'  )
    date = models.DateField(default=None, null=True)
    is_achieved = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} - {self.user}"
    # completamento del goal
    def achieve(self):
        self.is_achieved = True
        self.date = datetime.date.today()
        self.save()
    class Meta:
        verbose_name_plural = "goals"
        verbose_name = "goal"
        unique_together = ('name', 'user')
        ordering = ['name']

def days_in_this_year():
    if datetime.date.today().year % 4 == 0:
        return 366
    else:
        return 365

# Workout che compone una Progress_Sheet
class Workout(models.Model):
    date = models.DateField(
        validators=[
            MinValueValidator(datetime.date.today() - datetime.timedelta(days=31)),
            MaxValueValidator(datetime.date.today())]
    )
    calories_burned = models.DecimalField(
        help_text="Calories burned during the workout",
        validators=[MaxValueValidator(10000)],
        max_digits=6, decimal_places=1,
        default=0
    )
    description = models.CharField(null=True, blank=True, max_length=500)
    progress_sheet = models.ForeignKey('ProgressSheet', on_delete=models.CASCADE)
    @property
    def adjusted_caloric_burn(self):
        return self.calories_burned + self.progress_sheet.user.bmr
    def __str__(self):
        return f"{self.date} - {self.progress_sheet}"

    class Meta:
        verbose_name_plural = "workouts"
        verbose_name = "workout"
        ordering = ['progress_sheet', 'date']

class Feedback(models.Model):

    workout = models.OneToOneField('Workout', on_delete=models.CASCADE, parent_link=True, primary_key=True)

    comment = models.CharField(max_length=500)
    class Meta:
        verbose_name_plural = "feedbacks"
        verbose_name = "feedback"
        ordering = ['workout']

#manager delle istanze di Prog sheet
class ProgressSheetManager(models.Manager):
    def get_or_create_for_user_and_year(self, user, year):
        # Questo metodo proverà a recuperare una ProgressSheet esistente
        # per l'utente e l'anno specificati.
        # Se non esiste, ne creerà una nuova e la restituirà.
        sheet, created = self.get_or_create(user=user, year=year)
        return sheet
class ProgressSheet(models.Model):
    year = models.IntegerField(
        validators=[
            MinValueValidator(2025),
            MaxValueValidator(datetime.date.today().year)
            ]
    )
    user = models.ForeignKey('accounts.StandardUser', on_delete=models.CASCADE)

    objects = ProgressSheetManager()
    def __str__(self):
        return f"{self.year} - {self.user}"


    class Meta:
        verbose_name_plural = "progress_sheets"
        verbose_name = "progress_sheet"
        unique_together = ('year', 'user')
        order_with_respect_to = 'user'


class Feedback(models.Model):

    workout = models.OneToOneField('Workout', on_delete=models.CASCADE, parent_link=True, primary_key=True)

    comment = models.CharField(max_length=500)
    class Meta:
        verbose_name_plural = "feedbacks"
        verbose_name = "feedback"
        ordering = ['workout']

