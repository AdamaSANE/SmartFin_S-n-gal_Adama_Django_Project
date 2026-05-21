import os
import unicodedata
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from django.core.management.base import BaseCommand
from finance.models import Categorie, Transaction


def _normalize(s: str) -> str:
    """Normalise une chaîne (minuscules, sans accents) pour comparer les en-têtes."""
    if s is None:
        return ""
    s = str(s)
    nk = unicodedata.normalize('NFKD', s)
    return nk.encode('ascii', 'ignore').decode('ascii').lower().strip()


class Command(BaseCommand):
    help = 'Importe les transactions financières depuis un fichier CSV (tolérance sur les noms de colonnes)'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', help='Chemin vers le fichier CSV (par défaut: transactions_test.csv)')
        parser.add_argument('--dry-run', action='store_true', help="Ne sauvegarde pas les objets (test)")

    def handle(self, *args, **options):
        chemin_fichier = options.get('file') or 'transactions_test.csv'
        dry_run = options.get('dry_run', False)

        # Vérification du fichier
        if not os.path.exists(chemin_fichier):
            self.stderr.write(self.style.ERROR(f"Le fichier {chemin_fichier} est introuvable."))
            return

        # Lecture avec pandas si disponible, sinon fallback en csv.DictReader
        try:
            import pandas as pd

            def parse_date(s):
                if s is None:
                    return None
                s = str(s).strip()
                if s == '':
                    return None
                # Try ISO first
                try:
                    return datetime.strptime(s, '%Y-%m-%d').date()
                except Exception:
                    pass
                # Common other formats
                for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y'):
                    try:
                        return datetime.strptime(s, fmt).date()
                    except Exception:
                        continue
                # Last resort: try to parse just year-month-day with replace
                # If not parsable, return None
                return None

            df = pd.read_csv(chemin_fichier)
            # Construire une map des colonnes normalisées -> nom original
            col_map = { _normalize(c): c for c in df.columns }

            def get_val(row, *candidates):
                for cand in candidates:
                    key = _normalize(cand)
                    if key in col_map:
                        return row[col_map[key]]
                return None

            compteur = 0
            for idx, row in df.iterrows():
                # Récupération tolérante des champs
                # Ignorer les lignes qui sont en fait des en-têtes ré-insertées
                header_tokens = { 'date', 'montant', 'amount', 'type', 'description', 'categorie', 'category', 'transaction_id' }
                row_values_normalized = { _normalize(v) for v in row.values }
                if header_tokens & row_values_normalized:
                    self.stdout.write(self.style.NOTICE(f"Ignorée ligne d'en-tête insérée (index {idx})"))
                    continue
                cat_nom = get_val(row, 'categorie', 'catégorie', 'category') or 'Sans catégorie'
                date_val = get_val(row, 'date', 'date_transaction', 'transaction_date')
                montant_val = get_val(row, 'montant', 'amount')
                type_val = get_val(row, 'type', 'type_transaction', 'transaction_type')
                description = get_val(row, 'description', 'desc') or ''

                # Nettoyage des espaces non imprimables
                def _clean(v):
                    if v is None:
                        return v
                    return str(v).strip().replace('\xa0', ' ')

                date_val = _clean(date_val)
                montant_val = _clean(montant_val)
                type_val = _clean(type_val)
                description = _clean(description)

                # Fonctions d'inférence
                import re
                def is_iso_date(s):
                    if s is None:
                        return False
                    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(s).strip()))

                def looks_like_amount(s):
                    if s is None:
                        return False
                    return bool(re.match(r"^-?\s*\d+[\.,]?\d*$", str(s).strip()))

                # Si les colonnes sont mal mappées, tenter d'inférer par contenu
                if not is_iso_date(date_val):
                    for orig_col in df.columns:
                        candidate = _clean(row[orig_col])
                        if is_iso_date(candidate):
                            date_val = candidate
                            break

                if not looks_like_amount(montant_val):
                    for orig_col in df.columns:
                        candidate = _clean(row[orig_col])
                        if looks_like_amount(candidate):
                            montant_val = candidate
                            break
                # Normaliser le montant
                montant = None
                if montant_val is not None and str(montant_val).strip() != '':
                    try:
                        montant = Decimal(str(montant_val).replace(',', '.'))
                    except InvalidOperation:
                        montant = None

                # Parser / valider la date avant création
                date_obj = parse_date(date_val)
                if date_obj is None:
                    # essayer d'inférer par contenu déjà fait; si toujours None, log et ignorer
                    self.stderr.write(self.style.ERROR(f"Échec création transaction (ligne {idx+2}): date invalide ou manquante: '{date_val}'"))
                    continue
                date_transaction = date_obj

                # Déduire le type si absent
                if not type_val:
                    try:
                        if montant is not None and montant < 0:
                            type_transaction = 'DEPENSE'
                        else:
                            type_transaction = 'REVENU'
                    except Exception:
                        type_transaction = 'DEPENSE'
                else:
                    tv = str(type_val).strip().upper()
                    if 'REV' in tv or 'INCOM' in tv or 'CREDIT' in tv:
                        type_transaction = 'REVENU'
                    else:
                        type_transaction = 'DEPENSE'

                # Création / récupération de la catégorie
                if not dry_run:
                    categorie_obj, _ = Categorie.objects.get_or_create(nom=str(cat_nom))
                else:
                    categorie_obj = None

                # Création de la transaction (si montant ou date présents)
                if not dry_run:
                    try:
                        Transaction.objects.create(
                            date_transaction=date_transaction,
                            montant=montant if montant is not None else Decimal('0.00'),
                            type_transaction=type_transaction,
                            description=description,
                            categorie=categorie_obj,
                        )
                    except Exception as exc:
                        self.stderr.write(self.style.ERROR(f"Échec création transaction (ligne): {exc}"))
                        continue
                else:
                    # Mode dry-run: affiche ce qui serait créé
                    self.stdout.write(f"DRY RUN -> date={date_transaction} montant={montant} type={type_transaction} desc='{description}' categorie='{cat_nom}'")

                compteur += 1

            self.stdout.write(self.style.SUCCESS(f"Succès ! {compteur} transactions traitées ({'dry-run' if dry_run else 'import'})."))

        except ImportError:
            # Fallback sans pandas
            import csv

            with open(chemin_fichier, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # normaliser en-têtes
                headers = { _normalize(h): h for h in reader.fieldnames }

                def get_val_dict(row, *candidates):
                    for cand in candidates:
                        key = _normalize(cand)
                        if key in headers:
                            return row[headers[key]]
                    return None

                compteur = 0
                for line_no, row in enumerate(reader, start=2):
                    cat_nom = get_val_dict(row, 'categorie', 'catégorie', 'category') or 'Sans catégorie'
                    date_val = get_val_dict(row, 'date', 'date_transaction', 'transaction_date')
                    montant_val = get_val_dict(row, 'montant', 'amount')
                    type_val = get_val_dict(row, 'type', 'type_transaction', 'transaction_type')
                    description = get_val_dict(row, 'description', 'desc') or ''

                    # Ignorer les lignes qui sont en fait des en-têtes ré-insertées
                    header_tokens = { 'date', 'montant', 'amount', 'type', 'description', 'categorie', 'category', 'transaction_id' }
                    row_vals_norm = { _normalize(v) for v in row.values() }
                    if header_tokens & row_vals_norm:
                        self.stdout.write(self.style.NOTICE(f"Ignorée ligne d'en-tête insérée (ligne {line_no})"))
                        continue

                    # Nettoyage et heuristiques similaires à la branche pandas
                    def _clean(v):
                        if v is None:
                            return v
                        return str(v).strip().replace('\xa0', ' ')

                    date_val = _clean(date_val)
                    montant_val = _clean(montant_val)
                    type_val = _clean(type_val)
                    description = _clean(description)

                    import re
                    def is_iso_date(s):
                        if s is None:
                            return False
                        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(s).strip()))

                    def looks_like_amount(s):
                        if s is None:
                            return False
                        return bool(re.match(r"^-?\s*\d+[\.,]?\d*$", str(s).strip()))

                    # Inférence par contenu si besoin
                    if not is_iso_date(date_val):
                        for h in reader.fieldnames:
                            candidate = _clean(row.get(h))
                            if is_iso_date(candidate):
                                date_val = candidate
                                break

                    if not looks_like_amount(montant_val):
                        for h in reader.fieldnames:
                            candidate = _clean(row.get(h))
                            if looks_like_amount(candidate):
                                montant_val = candidate
                                break

                    montant = None
                    if montant_val is not None and str(montant_val).strip() != '':
                        try:
                            montant = Decimal(str(montant_val).replace(',', '.'))
                        except InvalidOperation:
                            montant = None

                    if not type_val:
                        try:
                            if montant is not None and montant < 0:
                                type_transaction = 'DEPENSE'
                            else:
                                type_transaction = 'REVENU'
                        except Exception:
                            type_transaction = 'DEPENSE'
                    else:
                        tv = str(type_val).strip().upper()
                        if 'REV' in tv or 'INCOM' in tv or 'CREDIT' in tv:
                            type_transaction = 'REVENU'
                        else:
                            type_transaction = 'DEPENSE'

                    # Parser / valider la date avant création
                    def parse_date_local(s):
                        if s is None:
                            return None
                        s = str(s).strip()
                        if s == '':
                            return None
                        try:
                            return datetime.strptime(s, '%Y-%m-%d').date()
                        except Exception:
                            pass
                        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y'):
                            try:
                                return datetime.strptime(s, fmt).date()
                            except Exception:
                                continue
                        return None

                    date_obj = parse_date_local(date_val)
                    if date_obj is None:
                        self.stderr.write(self.style.ERROR(f"Échec création transaction (ligne {line_no}): date invalide ou manquante: '{date_val}'"))
                        # sauter l'enregistrement
                        continue
                    
                    if not dry_run:
                        try:
                            categorie_obj, _ = Categorie.objects.get_or_create(nom=str(cat_nom))
                            Transaction.objects.create(
                                date_transaction=date_obj,
                                montant=montant if montant is not None else Decimal('0.00'),
                                type_transaction=type_transaction,
                                description=description,
                                categorie=categorie_obj,
                            )
                        except Exception as exc:
                            self.stderr.write(self.style.ERROR(f"Échec création transaction (ligne): {exc}"))
                            continue
                    else:
                        self.stdout.write(f"DRY RUN -> date={date_val} montant={montant} type={type_transaction} desc='{description}' categorie='{cat_nom}'")

                    compteur += 1

                self.stdout.write(self.style.SUCCESS(f"Succès ! {compteur} transactions traitées ({'dry-run' if dry_run else 'import'})."))