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
            'email',
            'height',
            'weight',
            'biogender',
            'birth_date',
            'profile_picture',
            'first_name',
            'last_name',
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
    """
    Form personalizzato per la modifica di un utente esistente.
    Estende UserChangeForm di Django. Questo form è ideale per l'admin o per la modifica del profilo utente.
    """
    class Meta:
        model = StandardUser

        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'height', 'weight', 'biogender', 'birth_date', 'profile_picture',
        )
        labels = {
            'height': 'Altezza (cm)',
            'weight': 'Peso (kg)',
            'biogender': 'Sesso Biologico',
            'birth_date': 'Data di Nascita',
            'profile_picture': 'Immagine del Profilo',
            'is_coach': 'È Coach?',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AdminUserChangeForm(UserChangeForm):
    """Form for administrators to edit user profiles"""
    class Meta:
        model = StandardUser
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
            'height', 'weight', 'biogender', 'birth_date', 
            'profile_picture', 'is_coach',
            'groups', 'user_permissions',
        )