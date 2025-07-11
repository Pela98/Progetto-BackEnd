#fitness/views.py
from django.views.generic import UpdateView, ListView, DetailView
# --- Mixin per Admin ---



# --- Viste per Workout ---

# fitness/views.py

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Workout, ProgressSheet, Goal
from .forms import WorkoutForm, GoalForm
import datetime

class WorkoutCreateView(LoginRequiredMixin, CreateView):
    """
    Vista per permettere agli StandardUser di creare un nuovo workout.
    Associa automaticamente il workout alla ProgressSheet dell'anno corrente dell'utente.
    """
    model = Workout
    form_class = WorkoutForm
    template_name = 'fitness/workout_form.html'  # Creeremo questo template
    success_url = reverse_lazy('home')  # URL di successo dopo la creazione

    def form_valid(self, form):
        """
        Questo metodo viene chiamato quando il form è valido.
        Qui associamo il workout alla ProgressSheet corretta.
        """
        # Ottieni l'utente loggato
        user = self.request.user

        # Ottieni l'anno corrente
        current_year = datetime.date.today().year

        # Cerca o crea la ProgressSheet per l'utente e l'anno corrente
        # get_or_create restituisce l'oggetto e un booleano (creato o meno)
        progress_sheet, created = ProgressSheet.objects.get_or_create(
            user=user,
            year=current_year
        )
        if created:
            print(f"Created new ProgressSheet for user {user.username} for year {current_year}")

        # Associa la ProgressSheet al workout prima di salvarlo
        workout = form.save(commit=False) # Non salvare ancora nel database
        workout.progress_sheet = progress_sheet
        workout.save() # Ora salva l'istanza del workout

        return super().form_valid(form)


class GoalCreateUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista per permettere agli StandardUser di creare o aggiornare il proprio Goal.
    Poiché Goal ha una relazione OneToOne con l'utente e usa l'utente come PK,
    questa vista gestisce sia la creazione che la modifica per l'utente loggato.
    """
    model = Goal
    form_class = GoalForm
    template_name = 'fitness/goal_form.html'  # Creeremo questo template
    success_url = reverse_lazy('home')  # URL di successo dopo la creazione/modifica

    def get_object(self, queryset=None):
        """
        Recupera il Goal esistente per l'utente corrente, o restituisce None se non esiste.
        Questo metodo è fondamentale per la UpdateView per sapere quale oggetto modificare.
        """
        # Cerchiamo un Goal che abbia come primary key (PK) l'ID dell'utente corrente.
        # Poiché user è OneToOneField e primary_key=True, l'ID del Goal è l'ID dell'utente.
        try:
            return Goal.objects.get(pk=self.request.user.pk)
        except Goal.DoesNotExist:
            return None  # Nessun goal esistente, quindi lo creeremo

    def form_valid(self, form):
        """
        Questo metodo viene chiamato quando il form è valido.
        Qui associamo il Goal all'utente corrente prima del salvataggio.
        """
        goal = form.save(commit=False)
        goal.user = self.request.user  # Associa il Goal all'utente loggato
        goal.pk = self.request.user.pk  # Imposta la PK del Goal all'ID dell'utente (per la relazione OneToOne)
        goal.save()  # Ora salva l'istanza del Goal nel database
        return super().form_valid(form)

    # --- Viste per User Visualization ---

class UserProgressSheetListView(LoginRequiredMixin, ListView):
    model = ProgressSheet
    template_name = 'fitness/user_progress_sheets.html'
    context_object_name = 'progress_sheets'

    def get_queryset(self):
        current_year = datetime.date.today().year
        # Assicurati che la progress sheet dell'anno corrente esista per l'utente
        ProgressSheet.get_or_create_for_user_and_year(self.request.user, current_year)
        # Poi, recupera tutte le progress sheet dell'utente loggato
        return ProgressSheet.objects.filter(user=self.request.user).order_by('-year')

class ProgressSheetDetailView(LoginRequiredMixin, DetailView):
    """
    Vista per visualizzare i dettagli di una specifica ProgressSheet e tutti i suoi Workout.
    """
    model = ProgressSheet
    template_name = 'fitness/progress_sheet_detail.html'  # Questo sarà il nostro template
    context_object_name = 'progress_sheet'

    def get_queryset(self):
        # Assicurati che l'utente possa vedere solo le PROPRIE progress sheet.
        # Questo previene che un utente acceda alle schede di altri modificando l'ID nell'URL.
        return ProgressSheet.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        # Aggiunge i workout associati a questa ProgressSheet al contesto.
        context = super().get_context_data(**kwargs)
        context['workouts'] = self.object.workout_set.all().order_by('-date')
        context['title'] = f"Workouts di {self.object.year}"
        return context