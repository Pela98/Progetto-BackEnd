# accounts/forms.py
import os

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import StandardUser # Importa il tuo modello utente personalizzato

class StandardUserCreationForm(UserCreationForm):
    """
    Form personalizzato per la creazione di un nuovo utente (registrazione).
    Estende UserCreationForm di Django.
    """
    class Meta:
        model = StandardUser
       
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'height',
            'weight',
            'biogender',
            'birth_date',
            'profile_picture',

        )
        labels = {
            'username': 'Nome Utente',
            'email': 'Email',
            'height': 'Altezza (cm)',
            'weight': 'Peso (kg)',
            'biogender': 'Sesso Biologico',
            'birth_date': 'Data di Nascita',
            'profile_picture': 'Immagine del Profilo',
            'first_name': 'Nome',
            'last_name': 'Cognome',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class StandardUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
         del self.fields['password']
    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Solo file JPG e PNG sono permessi.")
            
            # Check file size (5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("L'immagine non può superare 5MB")
            
            return image

    class Meta:
        model = StandardUser

        fields = (
            'username',

            'email',
            'first_name',
            'last_name',
            'height', 'weight', 'biogender', 'birth_date', 'profile_picture',
            'is_coach',
        )
        labels = {
            'height': 'Altezza (cm)',
            'weight': 'Peso (kg)',
            'biogender': 'Sesso Biologico',
            'birth_date': 'Data di Nascita',
            'profile_picture': 'Immagine del Profilo',
            'is_coach': 'Sono un Coach',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

