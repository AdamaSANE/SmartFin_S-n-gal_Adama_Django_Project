from rest_framework import serializers
from .models import Categorie, Transaction

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description']

class TransactionSerializer(serializers.ModelSerializer):
    # Astuce : On récupère directement le nom en texte de la catégorie
    # plutôt que de renvoyer un simple numéro d'ID incompréhensible
    categorie_nom = serializers.ReadOnlyField(source='categorie.nom')

    class Meta:
        model = Transaction
        fields = [
            'id', 
            'date_transaction', 
            'montant', 
            'type_transaction', 
            'description', 
            'categorie_nom', 
            'date_enregistrement'
        ]