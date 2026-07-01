from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import CRMA, BureauLocal, Profil
from .forms import CRMAForm, BureauLocalForm, UserCreationFormCustom, ProfilForm
from .decorators import role_required


def connexion(request):
    """Page de connexion commune à tous les rôles."""
    if request.user.is_authenticated:
        return redirect('tableau_de_bord')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('tableau_de_bord')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")

    return render(request, 'core/connexion.html')


@login_required
def deconnexion(request):
    """Déconnexion et retour à la page de connexion."""
    logout(request)
    return redirect('connexion')


@login_required
def tableau_de_bord(request):
    """
    Redirige vers le bon tableau de bord selon le rôle de l'utilisateur.
    """
    try:
        role = request.user.profil.role
    except Exception:
        logout(request)
        messages.error(request, "Profil introuvable. Contactez l'administrateur.")
        return redirect('connexion')

    if role == 'superuser':
        return render(request, 'core/dashboard_superuser.html')
    elif role == 'sous_superuser':
        return render(request, 'core/dashboard_sous_superuser.html')
    else:
        return render(request, 'core/dashboard_utilisateur.html')
    
# ─── Gestion des CRMA (super-utilisateur national uniquement) ─────────────────

@role_required('superuser')
def crma_liste(request):
    crmas = CRMA.objects.all().order_by('code')
    return render(request, 'core/crma_liste.html', {'crmas': crmas})


@role_required('superuser')
def crma_creer(request):
    if request.method == 'POST':
        form = CRMAForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "CRMA créée avec succès.")
            return redirect('crma_liste')
    else:
        form = CRMAForm()
    return render(request, 'core/crma_form.html', {'form': form, 'titre': 'Créer une CRMA'})


@role_required('superuser')
def crma_modifier(request, pk):
    crma = get_object_or_404(CRMA, pk=pk)
    if request.method == 'POST':
        form = CRMAForm(request.POST, instance=crma)
        if form.is_valid():
            form.save()
            messages.success(request, "CRMA modifiée avec succès.")
            return redirect('crma_liste')
    else:
        form = CRMAForm(instance=crma)
    return render(request, 'core/crma_form.html', {'form': form, 'titre': f'Modifier {crma.nom}'})


@role_required('superuser')
def crma_supprimer(request, pk):
    crma = get_object_or_404(CRMA, pk=pk)
    if request.method == 'POST':
        crma.delete()
        messages.success(request, "CRMA supprimée.")
        return redirect('crma_liste')
    return render(request, 'core/crma_confirmer_suppression.html', {'objet': crma})