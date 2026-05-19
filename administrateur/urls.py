from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('ajouter-caisse/', views.ajouter_caisse, name='ajouter_caisse'),
]