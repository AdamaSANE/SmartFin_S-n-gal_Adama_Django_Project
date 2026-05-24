from django.urls import path
from . import views

urlpatterns = [
    # Notre nouvelle page visuelle (Le tableau de bord Bootstrap)
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Tes routes API existantes
    path('categories/', views.CategorieListCreate.as_view(), name='categorie-list'),
    path('transactions/', views.TransactionListCreate.as_view(), name='transaction-list'),
]