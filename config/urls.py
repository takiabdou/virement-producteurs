from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('dashboard/', views.tableau_de_bord, name='tableau_de_bord'),
    # Gestion des CRMA
    path('crmas/', views.crma_liste, name='crma_liste'),
    path('crmas/creer/', views.crma_creer, name='crma_creer'),
    path('crmas/<int:pk>/modifier/', views.crma_modifier, name='crma_modifier'),
    path('crmas/<int:pk>/supprimer/', views.crma_supprimer, name='crma_supprimer'),
]