# SmartFin Sénégal - Application de Gestion et d'Analyse Financière

SmartFin est une application web robuste de gestion financière conçue pour automatiser le traitement, l'analyse et la visualisation de transactions financières. Ce projet intègre un pipeline ETL (Extract, Transform, Load) de données, une API REST sécurisée, et une interface utilisateur unifiée avec calculs d'indicateurs de performance (KPI) en temps réel.

Développé dans le cadre de la validation de la certification **CodingNomads (Session de Juin 2026)**.

---

## 🛠️ Installation et Configuration

Suivez ces étapes pour installer et exécuter le projet dans votre environnement local :

1. Activation de l'environnement virtuel

   Sur Windows :

   ```bash
   .venv\Scripts\activate
   ```

   Sur macOS/Linux :

   ```bash
   source .venv/bin/activate
   ```

2. Installation des dépendances

   Assurez-vous d'installer toutes les bibliothèques requises :

   ```bash
   pip install django djangorestframework pandas openpyxl
   ```

3. Application des migrations

   Générez et appliquez la structure de la base de données :

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Création du compte Administrateur

   Créer un compte pour franchir le verrou de sécurité de l'interface :

   ```bash
   python manage.py createsuperuser
   ```

   Suivez les instructions dans le terminal pour définir votre nom d'utilisateur et votre mot de passe.

5. Lancement de l'application

   Démarrez le serveur de développement local :

   ```bash
   python manage.py runserver
   ```

---

## 🖥️ Utilisation de l'Application

Une fois le serveur démarré, ouvrez votre navigateur et accédez aux adresses suivantes :

- Tableau de bord sécurisé (Interface UI) : http://127.0.0.1:8000/api/dashboard/
- Si vous n'êtes pas connecté, le système vous redirigera automatiquement vers la page de connexion.
- API REST - Liste des Catégories (JSON) : http://127.0.0.1:8000/api/categories/
- API REST - Liste des Transactions (JSON) : http://127.0.0.1:8000/api/transactions/
- Interface d'Administration Django : http://127.0.0.1:8000/admin/

---

## 🚀 Fonctionnalités Clés

- **Architecture Backend Robuste :** Conçu avec Django, s'appuyant sur une base de données relationnelle SQLite parfaitement modélisée (relations Un-à-Plusieurs entre Catégories et Transactions).
- **Pipeline Data (ETL) :** Automatisation de l'ingestion de fichiers de transactions bruts grâce à un script basé sur la bibliothèque **Pandas**, nettoyant et injectant les données de manière fiable dans l'ORM Django.
- **API REST Personnalisée :** Exposition des données pures (Catégories et Transactions) au format JSON via **Django REST Framework (DRF)**, supportant nativement les méthodes de lecture (`GET`) et de création (`POST`).
- **Intelligence d'Affaires (KPIs) :** Un tableau de bord visuel calculant automatiquement les indicateurs financiers critiques (Total des revenus, Total des dépenses, Solde actuel) optimisé via des requêtes d'agrégation de base de données (`Sum`).
- **Rigueur Comptable :** Formatage de l'affichage monétaire configuré à deux chiffres après la virgule (`.00`) pour assurer une précision visuelle rigoureuse.
- **Sécurité et Authentification :** Protection de l'interface utilisateur grâce au système de session natif de Django et à l'utilisation de verrous applicatifs (`LoginRequiredMixin`).
- **Interface UI Moderne :** Design unifié, fluide et adaptatif conçu avec **Bootstrap 5**, offrant une expérience utilisateur professionnelle et claire.

---

## 📂 Architecture du Projet

```text
SmartFin_Sénégal_Adama_Django_Project/
 │
 ├── config/                  # Configuration principale du projet Django (settings, urls)
 │   └── templates/           # Gabarits HTML du projet
 │
 ├── finance/                 # Application principale de gestion financière
 │    ├── models.py           # Modèles de données (Categorie, Transaction)
 │    ├── serializers.py      # Traducteurs de modèles vers le format JSON (DRF)
 │    ├── views.py            # Logique backend (Vues Visuelles & Vues API REST)
 │    └── urls.py             # Routage interne de l'application finance
 │
 ├── config/templates/        # Gabarits HTML (Interface Visuelle)
 │    ├── base.html           # Structure globale unifiée (Navbar, Styles Bootstrap)
 │    ├── dashboard.html      # Tableau de bord, cartes KPI et historique des transactions
 │    └── registration/
 │         └── login.html     # Page de connexion sécurisée
 │
 ├── data/                    # Répertoire contenant les fichiers financiers bruts (CSV)
 ├── db.sqlite3               # Base de données relationnelle SQLite3
 └── manage.py                # Outil d'administration en ligne de commande de Django
```
