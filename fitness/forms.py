# fitness/forms.py

from django import forms
import datetime

from .models import Workout, Goal, Feedback # Importa solo i modelli che userai nei form

class WorkoutForm(forms.ModelForm):
    """
    Form per la creazione e modifica di un Workout.
    """
    class Meta:
        model = Workout
        fields = ['date', 'calories_burned', 'description'] # progress_sheet verrà messo nella view

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'date': 'Data dell\'allenamento',
            'calories_burned': 'Calorie bruciate',
            'description': 'Descrizione dell\'allenamento',
        }
        help_texts = {
            'calories_burned': 'Inserisci le calorie stimate bruciate durante l\'allenamento.',
        }
    def clean_date(self):
        date = self.cleaned_data['date']
        today = datetime.date.today()
        if date < (today - datetime.timedelta(days=31)):
            raise forms.ValidationError("Date cannot be more than 31 days in the past")
        if date > today:
            raise forms.ValidationError("Date cannot be in the future")
        return date
    def clean_calories_burned(self):
        calories = self.cleaned_data['calories_burned']
        if calories > 10000:
            raise forms.ValidationError("Calories burned cannot exceed 10,000")
        return calories

class GoalForm(forms.ModelForm):
    """
    Form per la creazione e modifica di un Goal.
    """
    class Meta:
        model = Goal
        fields = ['name', 'description', 'target_weight',]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'maxlength':500}), # Casella di testo più grande per la descrizione
        }
        labels = {
            'name': 'Nome dell\'obiettivo',
            'description': 'Descrizione dettagliata',
            'target_weight': 'Peso target (kg)',
        }
        help_texts = {
            'target_weight': 'Il peso che desideri raggiungere in chilogrammi.',
            'target_bmi': 'L\'indice di massa corporea che desideri raggiungere.',
        }
    def clean_target_weight(self):
        weight = self.cleaned_data['target_weight']
        if weight and (weight < 5 or weight > 700):
            raise forms.ValidationError("Target weight must be between 5 and 700 kg")
        return weight

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment'] # Il coach inserirà solo il commento
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Lascia il tuo feedback qui...'}),
        }

