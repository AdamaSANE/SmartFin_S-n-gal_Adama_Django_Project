from django.contrib import admin

from .models import Categorie, Transaction


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "description")
    search_fields = ("nom",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date_transaction", "type_transaction", "montant", "categorie")
    list_filter = ("type_transaction", "categorie", "date_transaction")
    search_fields = ("description",)