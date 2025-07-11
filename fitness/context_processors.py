from .models import Goal



def uncompleted_goals_processor(request):
    """
    Aggiunge gli obiettivi non completati dell'utente loggato al contesto di ogni richiesta.
    """
    uncompleted_goals = []
    if request.user.is_authenticated:
        uncompleted_goals = Goal.objects.filter(
            user=request.user,
            is_achieved=False
        ).order_by('name').select_related('user')

    return {
        'uncompleted_goals': uncompleted_goals
    }


def achieved_goals_processor(request):
    """
    Aggiunge gli obiettivi raggiunti dell'utente loggato al contesto di ogni richiesta.
    """
    achieved_goals = []
    if request.user.is_authenticated:
        # Recupera i goal raggiunti dell'utente corrente
        # Ordina dal più recente al meno recente
        achieved_goals = Goal.objects.filter(
            user=request.user,
            is_achieved=True
        ).order_by('-date').select_related('user')  # Ordina per data decrescente

    return {
        'achieved_goals': achieved_goals
    }