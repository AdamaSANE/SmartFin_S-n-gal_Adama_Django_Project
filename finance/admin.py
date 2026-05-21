from django.contrib import admin
from .models import Categorie, Transaction

# On enregistre nos modèles pour pouvoir les manipuler manuellement
admin.site.register(Categorie)
admin.site.register(Transaction)