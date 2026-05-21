from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Transaction(models.Model):
    # Définition des choix stricts pour éviter les erreurs de saisie
    TYPE_CHOICES = [
        ('REVENU', 'Revenu'),
        ('DEPENSE', 'Dépense'),
    ]

    date_transaction = models.DateField()
    # DecimalField est obligatoire pour la finance (FloatField crée des erreurs d'arrondi)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255)

    # La relation clé étrangère : une catégorie peut avoir plusieurs transactions
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='transactions')

    # Pour l'audit interne : savoir exactement quand la donnée a été injectée
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date_transaction} | {self.type_transaction} : {self.montant} FCFA"