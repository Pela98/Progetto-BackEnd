# myapp/mixins.py
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

class CoachRequiredMixin(AccessMixin):
    """
    Mixin che fornisce un metodo di controllo per verificare se l'utente è un coach.
    Questo controllo verrà chiamato dal metodo dispatch della vista che la usa.
    """
    def check_coach_permission(self):
        # La logica del controllo vero e proprio
        return hasattr(self.request.user, 'is_coach') and self.request.user.is_coach

    def handle_no_permission(self):
        # Questo metodo è di AccessMixin e gestisce il reindirizzamento se il permesso manca
        if not self.request.user.is_authenticated:
            # Se non autenticato, usa la gestione predefinita di AccessMixin (solitamente redirect al login)
            return super().handle_no_permission()
        else:
            # Se autenticato ma non è un coach, reindirizza alla homepage
            return redirect(reverse_lazy('home'))