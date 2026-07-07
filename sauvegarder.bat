@echo off
title Sauvegarde Virement Producteurs
echo.
echo  Sauvegarde de la base de donnees...

:: Creer le dossier de sauvegardes
if not exist "sauvegardes" mkdir sauvegardes

:: Nom du fichier avec date et heure
set DATETIME=%date:~6,4%-%date:~3,2%-%date:~0,2%_%time:~0,2%h%time:~3,2%
set FICHIER=sauvegardes\backup_%DATETIME%.sql

:: Lancer pg_dump dans le conteneur Docker
docker exec virement_db pg_dump -U virement_user virement_producteurs > "%FICHIER%"

echo  Sauvegarde terminee : %FICHIER%
echo.
pause