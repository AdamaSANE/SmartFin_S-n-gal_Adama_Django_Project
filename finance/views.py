from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin  # Notre fameux "videur"
from rest_framework import generics

from .models import Transaction, Categorie
from .serializers import TransactionSerializer, CategorieSerializer

# ==========================================
# 1. LA VUE VISUELLE (HTML pour le navigateur)
# ==========================================
class DashboardView(LoginRequiredMixin, TemplateView):
    # Le videur (LoginRequiredMixin) est bien placé en premier
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        # On récupère le contexte de base
        context = super().get_context_data(**kwargs)
        
        # 1. Récupération de toutes les transactions
        transactions = Transaction.objects.all().order_by('-date_transaction')
        context['transactions'] = transactions
        
        # 2. Calcul Automatique (KPIs)
        revenus = transactions.filter(type_transaction='REVENU').aggregate(Sum('montant'))['montant__sum'] or 0
        depenses = transactions.filter(type_transaction='DEPENSE').aggregate(Sum('montant'))['montant__sum'] or 0
        
        # 3. On emballe les résultats pour les envoyer au template HTML
        context['total_revenus'] = revenus
        context['total_depenses'] = depenses
        context['solde'] = revenus - depenses
        
        return context


# ==========================================
# 2. LES VUES API (JSON pour les données pures)
# ==========================================
class CategorieListCreate(generics.ListCreateAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer


class TransactionListCreate(generics.ListCreateAPIView):
    queryset = Transaction.objects.all().order_by('-date_transaction')
    serializer_class = TransactionSerializer