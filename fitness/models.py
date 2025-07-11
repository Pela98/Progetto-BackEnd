#fitness/models.py

import datetime
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models



#scelte

#\scelte

class Goal(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    target_weight = models.DecimalField(default=None, null=True, max_digits=4, decimal_places=1, validators=[MinValueValidator(5), MaxValueValidator(700)])
    target_bmi = models.DecimalField( max_digits=4, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    # l'istanza di goal è riferita ad un user
    user= models.OneToOneField('accounts.StandardUser', on_delete=models.CASCADE, primary_key=True, parent_link=True)
    is_achieved = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    # quando un goal viene completato allora viene distrutto il record e viene creato
    def achieve(self):
        achievement = Achievement.objects.create(name=self.name, description=self.description, target_weight=self.target_weight, target_bmi=self.target_bmi, user=self.user, is_achieved=True, date=datetime.date.today())
        achievement.save()
        self.delete()
        return achievement
    class Meta:
        verbose_name_plural = "goals"
        verbose_name = "goal"
        ordering = ['user__username', 'name']


# quando un Goal è completato diventa un achievement
class Achievement(Goal):
    date = models.DateField(validators=[MinValueValidator(datetime.date.today() - datetime.timedelta(days=366)),])
    class Meta:
        verbose_name_plural = "achievements"
        verbose_name = "achievement"
        order_with_respect_to = 'date'
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
class ProgressSheet(models.Model):
    year = models.IntegerField(
        validators=[
            MinValueValidator(2025),
            MaxValueValidator(datetime.date.today().year)
            ]
    )
    user = models.ForeignKey('accounts.StandardUser', on_delete=models.CASCADE)
    @property
    def goal(self):
        return self.user.goal

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

