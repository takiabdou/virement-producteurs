@echo off
title Virement Producteurs - Serveur CRMA
color 1F
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                                                          ║
echo  ║   VIREMENT PRODUCTEURS - SERVEUR                         ║
echo  ║   Nom du serveur: %COMPUTERNAME%                         ║
echo  ║                                                          ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

call "%~dp0venv\Scripts\activate.bat"

echo  [1/3] Verification de la base de donnees...
docker ps | findstr "virement_db" >nul 2>&1
if errorlevel 1 (
    echo  Demarrage de PostgreSQL...
    docker compose up -d
    timeout /t 5 /nobreak >nul
) else (
    echo  Base de donnees active.
)

echo  [2/3] Verification des migrations...
python manage.py migrate --run-syncdb >nul 2>&1

echo  [3/3] Demarrage du serveur Django...
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║  Serveur demarre avec succes !                           ║
echo  ║                                                          ║
echo  ║  Accès local:     http://localhost:8000                  ║
echo  ║  Accès reseau:    http://%COMPUTERNAME%:8000             ║
echo  ║                                                          ║
echo  ║  Pour les clients:                                       ║
echo  ║  http://C45-276-Poste01:8000                             ║
echo  ║                                                          
echo  ║  Pour arreter: fermez cette fenetre                      ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

start http://localhost:8000/

python manage.py runserver 0.0.0.0:8000