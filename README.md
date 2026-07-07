# Virement Producteurs

Application web de gestion des versements producteurs pour les
Caisses Régionales de Mutualité Agricole (CRMA) d'Algérie.

## Prérequis

- Python 3.12
- Docker Desktop
- Git

## Installation sur un nouveau poste

```bash
git clone https://github.com/takiabdou/virement-producteurs.git
cd virement-producteurs
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Créez le fichier `.env` en copiant `.env.example` et en adaptant les valeurs.

```bash
docker compose up -d
python manage.py migrate
python manage.py createsuperuser
```

## Démarrage quotidien

Double-cliquez sur `demarrer.bat`

## Rôles utilisateurs

| Rôle | Accès |
|------|-------|
| Super-utilisateur | Gestion nationale de toutes les CRMA |
| Sous-super-utilisateur | Gestion des BL et agents d'une CRMA |
| Utilisateur BL | Brouillard de caisse et bons de versement |

## Stack technique

- Backend : Django 6 + Django REST Framework
- Base de données : PostgreSQL 16 (Docker)
- Frontend : HTML/CSS responsive (mobile + desktop)
- Déploiement : Windows 7/10/11 + Android (navigateur web)