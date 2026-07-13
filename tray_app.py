"""
Tray App - Virement Producteurs CRMA
Lance Django en arrière-plan avec une icône dans le system tray.
"""
import sys
import os
import subprocess
import webbrowser
from pathlib import Path

# ── Chemin du projet ──
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# ── Activer le venv ──
venv_python = BASE_DIR / "venv" / "Scripts" / "python.exe"
manage_py = BASE_DIR / "manage.py"

# ── Icône system tray ──
ICON_PATH = BASE_DIR / "core" / "static" / "core" / "img" / "favicon.ico"
if not ICON_PATH.exists():
    ICON_PATH = BASE_DIR / "favicon.ico"

# ── PyQt5 pour le system tray ──
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer


class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Icône
        self.icon = QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QIcon()

        # Menu contextuel
        self.tray = QSystemTrayIcon(self.icon)
        self.tray.setToolTip("Virement Producteurs CRMA")

        menu = QMenu()

        act_open = QAction("🌐 Ouvrir l'application", self.app)
        act_open.triggered.connect(self.open_browser)
        menu.addAction(act_open)

        menu.addSeparator()

        act_status = QAction("● Serveur actif — port 8000", self.app)
        act_status.setEnabled(False)
        menu.addAction(act_status)

        menu.addSeparator()

        act_restart = QAction("🔄 Redémarrer le serveur", self.app)
        act_restart.triggered.connect(self.restart_server)
        menu.addAction(act_restart)

        act_stop = QAction(" Arrêter le serveur", self.app)
        act_stop.triggered.connect(self.stop_server)
        menu.addAction(act_stop)

        menu.addSeparator()

        act_quit = QAction("✕ Quitter", self.app)
        act_quit.triggered.connect(self.quit_app)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

        # Message de bienvenue
        self.tray.showMessage(
            "Virement Producteurs",
            "Serveur démarré sur http://localhost:8000\n"
            "Cliquez sur l'icône pour les options.",
            QSystemTrayIcon.Information,
            4000
        )

        # Lancer Django
        self.django_process = None
        self.start_server()

    def start_server(self):
        """Lance le serveur Django en subprocess."""
        if self.django_process and self.django_process.poll() is None:
            return  # Déjà lancé

        try:
            self.django_process = subprocess.Popen(
                [str(venv_python), str(manage_py), "runserver", "0.0.0.0:8000"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            print(f"[OK] Serveur Django lancé (PID: {self.django_process.pid})")
        except Exception as e:
            print(f"[ERREUR] Impossible de lancer Django: {e}")

    def stop_server(self):
        """Arrête le serveur Django."""
        if self.django_process and self.django_process.poll() is None:
            self.django_process.terminate()
            self.django_process.wait()
            self.tray.showMessage("Serveur", "Serveur arrêté.", QSystemTrayIcon.Warning, 2000)
            print("[INFO] Serveur arrêté.")

    def restart_server(self):
        """Redémarre le serveur."""
        self.stop_server()
        import time
        time.sleep(1)
        self.start_server()
        self.tray.showMessage("Serveur", "Serveur redémarré.", QSystemTrayIcon.Information, 2000)

    def open_browser(self):
        """Ouvre le navigateur sur l'application."""
        webbrowser.open("http://localhost:8000/")

    def quit_app(self):
        """Quitte l'application."""
        self.stop_server()
        self.tray.hide()
        self.app.quit()


if __name__ == "__main__":
    tray = TrayApp()
    sys.exit(tray.app.exec_())