from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from datetime import datetime
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


@role_required('admin')
def admin_dashboard_view(request):
    """Dashboard admin avec totaux et opérations récentes."""
    total_grande_caisse = calcul_total('Grande Caisse')
    total_petite_caisse = calcul_total('Petite Caisse')
    total_caisse = total_grande_caisse + total_petite_caisse

    operations_grande = Caisse.objects.filter(type_caisse='Grande Caisse')[:10]
    operations_petite = Caisse.objects.filter(type_caisse='Petite Caisse')[:10]
    operations_recentes = Caisse.objects.all()[:10]

    context = {
        'total_caisse': total_caisse,
        'total_grande_caisse': total_grande_caisse,
        'total_petite_caisse': total_petite_caisse,
        'operations_grande': operations_grande,
        'operations_petite': operations_petite,
        'operations_recentes': operations_recentes,
    }
    return render(request, 'admin/dashboard.html', context)


@require_POST
@role_required('admin')
def ajouter_caisse(request):
    """Vue AJAX pour ajouter une opération de caisse."""
    try:
        type_caisse = request.POST.get("type_caisse")
        type_operation = request.POST.get("type")
        date = request.POST.get("date")
        motif = request.POST.get("motif")
        montant = request.POST.get("montant")

        # ===== Validation =====
        if not all([type_caisse, type_operation, date, motif, montant]):
            return JsonResponse({
                'success': False,
                'error': 'Tous les champs sont requis.'
            }, status=400)

        if type_caisse not in ['Grande Caisse', 'Petite Caisse']:
            return JsonResponse({
                'success': False,
                'error': 'Type de caisse invalide.'
            }, status=400)

        if type_operation not in ['Entrée', 'Sortie']:
            return JsonResponse({
                'success': False,
                'error': 'Type d\'opération invalide.'
            }, status=400)

        try:
            montant_float = float(montant)
            if montant_float <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Le montant doit être supérieur à zéro.'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Le montant doit être un nombre valide.'
            }, status=400)

        # Validation de la date
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Format de date invalide.'
            }, status=400)

        # ===== Création de l'opération =====
        caisse = Caisse.objects.create(
            type_caisse=type_caisse,
            type_operation=type_operation,
            date=date_obj,
            motif=motif,
            somme=montant_float,
        )

        # ===== Recalcul des totaux =====
        total_grande_caisse = calcul_total('Grande Caisse')
        total_petite_caisse = calcul_total('Petite Caisse')
        total_caisse = total_grande_caisse + total_petite_caisse

        return JsonResponse({
            'success': True,
            'message': 'Opération ajoutée avec succès.',
            'data': {
                'id': caisse.id,
                'type_caisse': caisse.type_caisse,
                'type_operation': caisse.type_operation,
                'date': caisse.date.strftime('%d/%m/%Y'),
                'motif': caisse.motif,
                'somme': float(caisse.somme),
            },
            'totaux': {
                'total_caisse': total_caisse,
                'total_grande_caisse': total_grande_caisse,
                'total_petite_caisse': total_petite_caisse,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Une erreur est survenue : {str(e)}'
        }, status=500)