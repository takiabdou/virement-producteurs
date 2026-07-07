@echo off
title Virement Producteurs
color 1F
echo.
echo  ================================================
echo   VIREMENT PRODUCTEURS - Demarrage du serveur
echo  ================================================
echo.

call "%~dp0venv\Scripts\activate.bat"

echo  Verification de la base de donnees...
docker ps | findstr "virement_db" >nul 2>&1
if errorlevel 1 (
    echo  Demarrage de PostgreSQL...
    docker compose up -d
    timeout /t 5 /nobreak >nul
) else (
    echo  Base de donnees active.
)

echo  Verification des migrations...
python manage.py migrate --run-syncdb >nul 2>&1

timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000/

echo.
echo  Serveur demarre : http://127.0.0.1:8000/
echo  Pour arreter : fermez cette fenetre
echo.
python manage.py runserver 0.0.0.0:8000