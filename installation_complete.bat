@echo off
chcp 65001 >nul
title Installation Virement Producteurs
color 0A

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   INSTALLATION - VIREMENT PRODUCTEURS CRMA       ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: ── ETAPE 1 : Verifier Python ──
echo  [1/7] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python non detecte. Installez Python 3.12.
    pause
    exit /b
)
echo    OK
echo.

:: ── ETAPE 2 : Demarrer Docker ──
echo  [2/7] Demarrage de PostgreSQL via Docker...
docker compose up -d
if errorlevel 1 (
    echo  [ERREUR] Docker Desktop n'est pas lance.
    echo  Lancez Docker Desktop et reessayez.
    pause
    exit /b
)
echo    OK - Attente du demarrage de la base...
timeout /t 5 /nobreak >nul
echo.

:: ── ETAPE 3 : Creer l'environnement virtuel ──
echo  [3/7] Creation de l'environnement virtuel...
if not exist "venv" (
    python -m venv venv
    echo    OK
) else (
    echo    Deja existant
)
echo.

:: ── ETAPE 4 : Installer les dependances ──
echo  [4/7] Installation des dependances...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo  [ERREUR] Echec installation dependances.
    pause
    exit /b
)
echo.

:: ── ETAPE 5 : Creer le fichier .env ──
echo  [5/7] Configuration du fichier .env...
if not exist ".env" (
    copy .env.example .env
    echo    Fichier .env cree a partir du modele.
    echo    IMPORTANT : Editez le fichier .env avec vos parametres.
    notepad .env
) else (
    echo    Fichier .env deja existant.
)
echo.

:: ── ETAPE 6 : Migrations ──
echo  [6/7] Application des migrations...
python manage.py migrate
if errorlevel 1 (
    echo  [ERREUR] Echec des migrations.
    pause
    exit /b
)
echo.

:: ── ETAPE 7 : Superutilisateur ──
echo  [7/7] Creation du superutilisateur...
python manage.py createsuperuser
echo.

:: ── FIN ──
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║                                                  ║
echo  ║   INSTALLATION TERMINEE !                        ║
echo  ║                                                  ║
echo  ║   Lancez demarrer.bat pour demarrer              ║
echo  ║   l'application.                                 ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.
pause