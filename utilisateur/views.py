from django.shortcuts import render
from django.db.models import Sum
from tresorerie.decorators import role_required
from tresorerie.models import Caisse


def calcul_total(type_caisse):
    """Calcule le total (entrées - sorties) pour une caisse donnée."""
    entrees = Caisse.objects.filter(
        type_caisse=type_caisse,
        type_operation='Entrée'
    ).aggregate(total=Sum('somme'))['total'] or 0

    sorties = Caisse.objects.filter(
        type_caisse=type_caisse,
        type_operation='Sortie'
    ).aggregate(total=Sum('somme'))['total'] or 0

    return float(entrees - sorties)


@role_required('utilisateur')
def user_dashboard_view(request):
    """
    Dashboard utilisateur en lecture seule.
    Affiche les totaux et les opérations, mais ne permet pas d'en ajouter.
    """
    total_grande_caisse = calcul_total('Grande Caisse')
    total_petite_caisse = calcul_total('Petite Caisse')
    total_caisse = total_grande_caisse + total_petite_caisse

    operations_grande = Caisse.objects.filter(type_caisse='Grande Caisse')[:20]
    operations_petite = Caisse.objects.filter(type_caisse='Petite Caisse')[:20]
    operations_recentes = Caisse.objects.all()[:20]

    context = {
        'total_caisse': total_caisse,
        'total_grande_caisse': total_grande_caisse,
        'total_petite_caisse': total_petite_caisse,
        'operations_grande': operations_grande,
        'operations_petite': operations_petite,
        'operations_recentes': operations_recentes,
    }
    return render(request, 'utilisateur/dashboard.html', context)