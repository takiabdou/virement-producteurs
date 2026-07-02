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
    # Gestion des Bureaux Locaux
    path('bureaux/', views.bl_liste, name='bl_liste'),
    path('bureaux/creer/', views.bl_creer, name='bl_creer'),
    path('bureaux/<int:pk>/modifier/', views.bl_modifier, name='bl_modifier'),
    path('bureaux/<int:pk>/supprimer/', views.bl_supprimer, name='bl_supprimer'),
    # Gestion des Utilisateurs BL
    path('utilisateurs/', views.utilisateur_liste, name='utilisateur_liste'),
    path('utilisateurs/creer/', views.utilisateur_creer, name='utilisateur_creer'),
    path('utilisateurs/<int:pk>/modifier/', views.utilisateur_modifier, name='utilisateur_modifier'),
    path('utilisateurs/<int:pk>/supprimer/', views.utilisateur_supprimer, name='utilisateur_supprimer'),
    # Brouillard de caisse
    path('brouillard/', views.brouillard, name='brouillard'),
    path('brouillard/ajouter/', views.encaissement_ajouter, name='encaissement_ajouter'),
    path('brouillard/<int:pk>/supprimer/', views.encaissement_supprimer, name='encaissement_supprimer'),
]