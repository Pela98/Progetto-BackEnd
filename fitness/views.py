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


class GoalCreateView(LoginRequiredMixin, CreateView):
    """
    Vista per creare un nuovo Goal per l'utente loggato.
    Dopo la creazione, controlla tutti i goal non completati dell'utente
    e lancia goal.achieve() se il BMI dell'utente raggiunge il target per uno di essi.
    """
    model = Goal
    form_class = GoalForm
    template_name = 'fitness/goal_form.html'  # Template per il form di creazione del goal

    def form_valid(self, form):
        # Associa l'utente al Goal che sta per essere creato
        goal = form.save(commit=False)
        goal.user = self.request.user
        goal.save()  # Salva il nuovo goal

        messages.success(self.request, f"Goal '{goal.name}' creato con successo!")

        # --- LOGICA PER IL CONTROLLO E L'ACHIEVEMENT DI TUTTI I GOAL NON COMPLETATI ---
        user = self.request.user

        # Recupera TUTTI i goal NON completati dell'utente
        uncompleted_goals = Goal.objects.filter(user=user, is_achieved=False)

        if user.height is not None and user.height > 0 and user.weight is not None:
            current_bmi = calculate_bmi(user.height, user.weight)

            if current_bmi is not None:
                # Itera su tutti i goal non completati
                for current_goal in uncompleted_goals:
                    if current_goal.target_weight is not None:
                        target_bmi = current_goal.target_bmi

        return super().form_valid(form)

    def get_success_url(self):
        # Dopo aver salvato il Goal, reindirizza l'utente a una pagina appropriata.
        # Ad esempio, la home o la pagina della Progress Sheet.
        return reverse_lazy('home')  # O un'altra URL rilevante, es. 'progress_sheet_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Crea un nuovo Goal"
        return context
    # --- Viste per User Visualization ---


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


class MarkGoalAchievedView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Vista per marcare un Goal specifico come raggiunto.
    Richiede l'ID del Goal nell'URL.
    """

    def test_func(self):
        # L'utente deve essere autenticato.
        # Il test effettivo sulla proprietà del goal avviene in dispatch.
        return self.request.user.is_authenticated

    def dispatch(self, request, *args, **kwargs):
        # Recupera il goal dall'ID nell'URL
        self.goal = get_object_or_404(Goal, pk=kwargs['pk'])

        # Controlla che l'utente loggato sia il proprietario del goal
        if self.goal.user != request.user:
            messages.error(request, "Non hai il permesso di completare questo obiettivo.")
            return redirect(reverse_lazy('home'))  # O una pagina di errore/precedente

        # Se il goal è già stato raggiunto, non fare nulla e reindirizza
        if self.goal.is_achieved:
            messages.info(request, f"L'obiettivo '{self.goal.name}' è già stato completato.")
            return redirect(
                request.META.get('HTTP_REFERER', reverse_lazy('home')))  # Reindirizza alla pagina precedente

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        # Chiama il metodo achieve() sul goal
        self.goal.achieve()
        messages.success(request, f"Congratulazioni! Hai completato l'obiettivo: '{self.goal.name}'!")

        # Reindirizza l'utente alla pagina da cui proveniva (o alla home se non è disponibile)
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('home')))

    def get_queryset(self):
        # Inizia filtrando solo i Goal che sono stati marcati come raggiunti.
        queryset = super().get_queryset().filter(is_achieved=True)

        # Logica dei permessi e del filtro per i coach:
        # Se l'utente corrente è un coach...
        if hasattr(self.request.user, 'is_coach') and self.request.user.is_coach:
            # Controlla se c'è un parametro 'user_id' nella query string (es. /achievements/?user_id=5)
            user_id_param = self.request.GET.get('user_id')
            if user_id_param:
                # Se un user_id è specificato, filtra per quell'utente.
                # Questo permette al coach di vedere gli achievement di un utente specifico.
                return queryset.filter(user_id=user_id_param).order_by('-date')
            else:
                # Se non c'è user_id, il coach vede tutti gli achievement di tutti gli utenti.
                # Ordina per data e poi per nome utente per una migliore leggibilità.
                return queryset.order_by('-date', 'user__username')

        # Se l'utente non è un coach, mostra solo i suoi achievement personali.
        return queryset.filter(user=self.request.user).order_by('-date')  # Ordina per data più recente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Titolo predefinito
        context['title'] = "I Tuoi Obiettivi Raggiunti"

        # Logica per visualizzare l'utente visualizzato se un coach sta filtrando
        user_id_param = self.request.GET.get('user_id')
        if user_id_param and hasattr(self.request.user, 'is_coach') and self.request.user.is_coach:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                # Cerca l'oggetto utente basandosi sull'ID fornito
                viewed_user = User.objects.get(pk=user_id_param)
                context['viewed_user'] = viewed_user
                context['title'] = f"Obiettivi Raggiunti di {viewed_user.username}"
            except User.DoesNotExist:
                # Se l'ID utente non corrisponde a un utente esistente, il titolo rimane quello di default
                messages.warning(self.request, "L'utente specificato non è stato trovato.")
                pass  # Non c'è bisogno di fare altro, il titolo rimane generico.

        return context

"""
class AchievedGoalsListView(LoginRequiredMixin, ListView):

    model = Goal
    template_name = 'fitness/achieved_goals_list.html'  # Questo sarà il template da creare
    context_object_name = 'achieved_goals'  # Il nome della variabile che useremo nel template

    def get_queryset(self):
        # Inizia filtrando solo i Goal che sono stati marcati come raggiunti.
        queryset = super().get_queryset().filter(is_achieved=True)

        # Logica dei permessi e del filtro per i coach:
        # Se l'utente corrente è un coach...
        if hasattr(self.request.user, 'is_coach') and self.request.user.is_coach:
            # Controlla se c'è un parametro 'user_id' nella query string (es. /achievements/?user_id=5)
            user_id_param = self.request.GET.get('user_id')
            if user_id_param:
                # Se un user_id è specificato, filtra per quell'utente.
                # Questo permette al coach di vedere gli achievement di un utente specifico.
                return queryset.filter(user_id=user_id_param).order_by('-date')
            else:
                # Se non c'è user_id, il coach vede tutti gli achievement di tutti gli utenti.
                # Ordina per data e poi per nome utente per una migliore leggibilità.
                return queryset.order_by('-date', 'user__username')

        # Se l'utente non è un coach, mostra solo i suoi achievement personali.
        return queryset.filter(user=self.request.user).order_by('-date')  # Ordina per data più recente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Titolo predefinito
        context['title'] = "I Tuoi Obiettivi Raggiunti"

        # Logica per visualizzare l'utente visualizzato se un coach sta filtrando
        user_id_param = self.request.GET.get('user_id')
        if user_id_param and hasattr(self.request.user, 'is_coach') and self.request.user.is_coach:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                # Cerca l'oggetto utente basandosi sull'ID fornito
                viewed_user = User.objects.get(pk=user_id_param)
                context['viewed_user'] = viewed_user
                context['title'] = f"Obiettivi Raggiunti di {viewed_user.username}"
            except User.DoesNotExist:
                # Se l'ID utente non corrisponde a un utente esistente, il titolo rimane quello di default
                messages.warning(self.request, "L'utente specificato non è stato trovato.")
                pass  # Non c'è bisogno di fare altro, il titolo rimane generico.

        return context
    """