# accounts/views.py
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin # Per le viste che richiedono login
from django.shortcuts import get_object_or_404

# Importa il tuo modello utente personalizzato
from .models import StandardUser
# Importa i form che abbiamo appena corretto
from .forms import StandardUserCreationForm, StandardUserChangeForm

class RegisterUserView(CreateView):
    """
    Vista per la registrazione di un nuovo utente.
    Usa StandardUserCreationForm per raccogliere i dati.
    """
    model = StandardUser
    form_class = StandardUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login') # Reindirizza l'utente alla pagina di login dopo la registrazione

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrati a FitnessTracker'
        return context
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registrazione completata con successo!')
        return response


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    
    model = StandardUser
    form_class = StandardUserChangeForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('home') # Reindirizza alla homepage

    def get_object(self, queryset=None):
        return get_object_or_404(StandardUser, pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifica il tuo Profilo'
        return context
    def form_invalid(self, form):
        messages.error(self.request, 'Si è verificato un errore. Controlla i dati inseriti.')
        return super().form_invalid(form)
