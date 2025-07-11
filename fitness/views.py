#fitness/views.py
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import UpdateView, ListView, DetailView


from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .mixins import CoachRequiredMixin
from .models import Workout, ProgressSheet, Goal, Feedback, calculate_bmi
from .forms import WorkoutForm, GoalForm, FeedbackForm
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

        user = self.request.user


        current_year = datetime.date.today().year

        # Cerca o crea la ProgressSheet per l'utente e l'anno corrente

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



class UserProgressSheetListView(LoginRequiredMixin, ListView):
    model = ProgressSheet
    template_name = 'fitness/user_progress_sheets.html'
    context_object_name = 'progress_sheets'

    def get_queryset(self):
        # Inizialmente, si assume che si stiano cercando le schede dell'utente loggato.
        target_user = self.request.user

        # Se l'utente è un coach E user_pk è fornito nell'URL,
        # significa che il coach sta cercando le schede di un altro utente.
        if hasattr(self.request.user, 'is_coach') and self.request.user.is_coach and 'user_pk' in self.kwargs:
            user_pk = self.kwargs['user_pk']
            # Recupera l'utente target o solleva un 404 se non esiste.
            target_user = get_object_or_404(get_user_model(), pk=user_pk)


        # Questa riga è importante per inizializzare la scheda se non esiste.
        current_year = datetime.date.today().year
        ProgressSheet.objects.get_or_create_for_user_and_year(target_user, current_year)

        # Recupera tutte le progress sheet dell'utente target, ordinate per anno.
        return ProgressSheet.objects.filter(user=target_user).order_by('-year')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Determina l'utente di cui stiamo visualizzando le schede per il titolo e il contesto.
        target_user = self.request.user
        if hasattr(self.request.user, 'is_coach') and self.request.user.is_coach and 'user_pk' in self.kwargs:
            user_pk = self.kwargs['user_pk']
            target_user = get_object_or_404(get_user_model(), pk=user_pk)

        context['title'] = f"Schede Progressi di {target_user.username}"
        context['target_user'] = target_user  # Passa l'utente di cui si visualizzano le schede al template

        # Aggiungi un flag per sapere se si sta visualizzando la propria scheda o quella di un altro
        context['is_own_sheet'] = (target_user == self.request.user)

        return context


class ProgressSheetDetailView(LoginRequiredMixin, DetailView):
    model = ProgressSheet
    template_name = 'fitness/progress_sheet_detail.html'
    context_object_name = 'progress_sheet'

    def get_queryset(self):
        # Questa logica è già corretta per i permessi:
        # i coach possono vedere tutte le schede, gli utenti normali solo le proprie.
        if hasattr(self.request.user, 'is_coach') and self.request.user.is_coach:
            return ProgressSheet.objects.all()
        return ProgressSheet.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # L'oggetto `self.object` è la ProgressSheet che è stata recuperata dalla get_queryset.
        # Possiamo ottenere l'utente proprietario della scheda da qui.
        sheet_owner = self.object.user

        workouts = self.object.workout_set.all().order_by('-date')

        workouts_with_feedback = []
        for workout in workouts:
            try:
                feedback = Feedback.objects.get(workout=workout)
            except Feedback.DoesNotExist:
                feedback = None

            workouts_with_feedback.append({
                'workout': workout,
                'feedback': feedback
            })

        context['workouts_with_feedback'] = workouts_with_feedback
        context['title'] = f"Workouts della Scheda {self.object.year} di {sheet_owner.username}"  # Titolo più specifico
        context['sheet_owner'] = sheet_owner  # Passa il proprietario della scheda al template

        # Determina se il bottone "Aggiungi Nuovo Workout" deve essere mostrato.
        # Lo mostri solo se l'utente loggato è il proprietario della scheda.
        context['can_add_workout'] = (self.request.user == sheet_owner)
        """achieved_goals = Goal.objects.filter(
            user=sheet_owner,
            is_achieved=True
        ).order_by('-date')
        unachieved_goal = Goal.objects.filter(
            user=sheet_owner,
            is_achieved=False
       
        )"""

        return context


User = get_user_model()
class UserListView(LoginRequiredMixin, CoachRequiredMixin, ListView):  # LoginRequiredMixin prima
    model = User
    template_name = 'fitness/user_list.html'
    context_object_name = 'all_users'

    def dispatch(self, request, *args, **kwargs):
        # Prima di tutto, esegui i controlli di LoginRequiredMixin
        # Questo assicura che l'utente sia autenticato
        response = super().dispatch(request, *args, **kwargs)

        # Dopo che LoginRequiredMixin ha fatto il suo lavoro (e l'utente è autenticato),
        # usiamo la logica della nostra CoachRequiredMixin.
        # check_coach_permission è disponibile tramite la mixin.
        if not self.check_coach_permission():
            return self.handle_no_permission()  # Questo reindirizzerà a 'home' se non è un coach

        # Se tutti i controlli passano, restituisci la risposta dal dispatch originale
        return response

    def get_queryset(self):
        return User.objects.all().order_by('username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Elenco di Tutti gli Utenti'
        return context


class FeedbackCreateUpdateView(LoginRequiredMixin, CoachRequiredMixin, CreateView):
    """
    Vista per i coach per creare o aggiornare un feedback per un workout specifico.
    Se un feedback esiste già per il workout, la vista funzionerà come UpdateView.
    """
    model = Feedback
    form_class = FeedbackForm
    template_name = 'fitness/feedback_form.html'  # Useremo questo template per il form

    # Il success_url sarà determinato dinamicamente dopo il salvataggio del form
    # per reindirizzare alla pagina di dettaglio della ProgressSheet corretta.

    def dispatch(self, request, *args, **kwargs):
        # Prima di tutto, esegui i controlli di autenticazione e permesso coach.
        response = super().dispatch(request, *args, **kwargs)
        if not self.check_coach_permission():  # Metodo dalla CoachRequiredMixin
            return self.handle_no_permission()
        return response

    def get_object(self, queryset=None):
        # Questo metodo è cruciale: tenta di recuperare un feedback esistente.
        # Se lo trova, la vista agirà come UpdateView; altrimenti, come CreateView.
        workout_pk = self.kwargs.get('workout_pk')
        workout = get_object_or_404(Workout, pk=workout_pk)

        try:
            # Cerca un feedback associato al workout. Assumiamo una relazione OneToOne.
            return Feedback.objects.get(workout=workout)
        except Feedback.DoesNotExist:
            return None  # Nessun feedback esistente, quindi la vista procederà alla creazione.

    def get_form_kwargs(self):
        # Se stiamo aggiornando (cioè self.object non è None), passiamo l'istanza al form.
        kwargs = super().get_form_kwargs()
        if self.object:  # self.object è il feedback esistente trovato da get_object()
            kwargs['instance'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout_pk = self.kwargs.get('workout_pk')
        workout = get_object_or_404(Workout, pk=workout_pk)
        context['workout'] = workout


        # Format the date using Python's strftime() method
        formatted_date = workout.date.strftime('%d %b %Y')  # e.g., '11 Jul 2025'

        if self.object:  # If we are modifying an existing feedback
            context['title'] = f"Modifica Feedback per Workout del {formatted_date}"
        else:  # If we are creating new feedback
            context['title'] = f"Lascia Feedback per Workout del {formatted_date}"
        # --- END CORRECTION ---

        return context

    def form_valid(self, form):
        # Associa il feedback al workout specifico prima di salvarlo.
        workout_pk = self.kwargs.get('workout_pk')
        workout = get_object_or_404(Workout, pk=workout_pk)

        feedback = form.save(commit=False)
        feedback.workout = workout  # Collega il feedback al workout corrente

        # Se `get_object` ha trovato un feedback esistente, ci assicuriamo di aggiornare quello.
        # Altrimenti, creerà un nuovo oggetto.
        if self.object:  # Se `self.object` è l'istanza esistente recuperata da `get_object`
            feedback.pk = self.object.pk  # Forza l'aggiornamento dell'istanza esistente

        feedback.save()  # Salva il feedback (crea o aggiorna)

        return super().form_valid(form)

    def get_success_url(self):
        # Dopo aver salvato il feedback, reindirizziamo alla pagina di dettaglio
        # della ProgressSheet a cui appartiene il workout.
        workout_pk = self.kwargs.get('workout_pk')
        workout = get_object_or_404(Workout, pk=workout_pk)
        return reverse('progress_sheet_detail', kwargs={'pk': workout.progress_sheet.pk})
############################l'interminabile tormento######################################
class GoalCreateView(LoginRequiredMixin, CreateView):
    """
    View per la creazione di un nuovo obiettivo.
    Associa automaticamente l'obiettivo all'utente loggato.
    """
    model = Goal
    form_class = GoalForm
    template_name = 'fitness/goal_form.html' # Crea questo template
    success_url = reverse_lazy('unachieved_goals_list') # Reindirizza alla lista degli obiettivi non raggiunti

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Il calcolo del target_bmi avviene come proprietà nel modello,
        # ma puoi assicurarti che il target_weight sia presente se necessario.
        response = super().form_valid(form)
        messages.success(self.request, "Obiettivo creato con successo!")
        return response

class GoalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View per la modifica di un obiettivo esistente.
    Permette solo al proprietario dell'obiettivo o a un coach di modificarlo.
    """
    model = Goal
    form_class = GoalForm
    template_name = 'fitness/goal_form.html' # Puoi usare lo stesso template della creazione
    context_object_name = 'goal' # Il nome dell'oggetto nel template
    success_url = reverse_lazy('unachieved_goals_list') # Reindirizza alla lista degli obiettivi non raggiunti

    def test_func(self):
        goal = self.get_object()
        return self.request.user == goal.user or self.request.user.is_coach

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Obiettivo aggiornato con successo!")
        return response

    def get_queryset(self):
        # Per i coach, mostriamo tutti gli obiettivi
        if self.request.user.is_coach:
            return Goal.objects.all()
        # Per gli utenti normali, mostriamo solo i loro obiettivi
        return Goal.objects.filter(user=self.request.user)


def achieve_goal(request, pk):
    """
    Funzione per marcare un obiettivo come raggiunto.
    """
    goal = get_object_or_404(Goal, pk=pk)
    # Controlla che solo il proprietario o un coach possano marcare l'obiettivo come raggiunto
    if request.user != goal.user:
        messages.error(request, "Non hai il permesso di completare questo obiettivo.")
        return redirect('unachieved_goals_list') # Reindirizza dove preferisci in caso di errore
    goal.is_achieved = True
    goal.save()
    messages.success(request, f"Obiettivo '{goal.name}' segnato come raggiunto!")
    return redirect('home') # Reindirizza alla lista degli obiettivi raggiunti


class BaseGoalListView(LoginRequiredMixin, ListView):
    """
    Classe base per la visualizzazione delle liste di obiettivi.
    Gestisce la logica di filtro per coach e utenti normali.
    """
    model = Goal
    context_object_name = 'goals'
    template_name = 'fitness/goal_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()



        return queryset.filter(user=self.request.user)

class AchievedGoalsListView(BaseGoalListView):
    """
    View per listare gli obiettivi già raggiunti.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_achieved=True)

class UnachievedGoalsListView(BaseGoalListView):
    """
    View per listare gli obiettivi non ancora raggiunti.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_achieved=False)

class UserGoalsListView(LoginRequiredMixin, CoachRequiredMixin, ListView): # Aggiungi CoachRequiredMixin se solo i coach possono vederla
    model = Goal
    context_object_name = 'goals'
    template_name = 'fitness/user_specific_goals_list.html' # Useremo un nuovo template per chiarezza

    def get_queryset(self):
        user_pk = self.kwargs['user_pk'] # Ottiene l'ID utente dall'URL
        viewed_user = get_object_or_404(User, pk=user_pk) # Assicurati che l'utente esista

        # Logica di permesso: un coach può vedere gli obiettivi di qualsiasi utente.
        # Un utente normale può vedere solo i propri obiettivi.
        if self.request.user.is_coach: # Assumendo 'is_coach' sul modello User
            return Goal.objects.filter(user=viewed_user).order_by('-is_achieved', 'name') # Ordina come preferisci
        elif self.request.user == viewed_user:
            # Se è l'utente stesso (non coach), gli permette di vedere i suoi obiettivi
            return Goal.objects.filter(user=viewed_user).order_by('-is_achieved', 'name')
        else:
            # Se non è un coach e sta cercando di vedere obiettivi di un altro, nega l'accesso.
            # Questo è gestito dalla CoachRequiredMixin se l'hai aggiunta sopra,
            # ma è una buona ridondanza o fallback.
            # Potresti anche sollevare una Http404 o reindirizzare.
            # Per ora, restituiamo un queryset vuoto o reindirizziamo come fa la mixin.
            self.handle_no_permission() # Delega alla AccessMixin per gestire l'errore/reindirizzamento
            return Goal.objects.none() # Restituisce un queryset vuoto per sicurezza

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pk = self.kwargs['user_pk']
        viewed_user = get_object_or_404(User, pk=user_pk)
        context['viewed_user'] = viewed_user # Passa l'oggetto utente al template
        context['title'] = f"Obiettivi di {viewed_user.username}"
        return context