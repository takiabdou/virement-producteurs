from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import CRMA, BureauLocal, Profil
from .forms import CRMAForm, BureauLocalForm, UserCreationFormCustom, UserModificationForm, ProfilForm
from .decorators import role_required
from django.contrib.auth.models import User
from django import forms

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

# ─── Gestion des Bureaux Locaux (sous-super-utilisateur CRMA) ─────────────────

@role_required('sous_superuser')
def bl_liste(request):
    crma = request.user.profil.crma
    bureaux = BureauLocal.objects.filter(crma=crma).order_by('code')
    return render(request, 'core/bl_liste.html', {'bureaux': bureaux, 'crma': crma})


@role_required('sous_superuser')
def bl_creer(request):
    crma = request.user.profil.crma
    if request.method == 'POST':
        form = BureauLocalForm(request.POST)
        if form.is_valid():
            bl = form.save(commit=False)
            bl.crma = crma
            bl.save()
            messages.success(request, "Bureau Local créé avec succès.")
            return redirect('bl_liste')
    else:
        form = BureauLocalForm()
    return render(request, 'core/bl_form.html', {
        'form': form, 'titre': 'Créer un Bureau Local', 'crma': crma
    })


@role_required('sous_superuser')
def bl_modifier(request, pk):
    crma = request.user.profil.crma
    bl = get_object_or_404(BureauLocal, pk=pk, crma=crma)
    if request.method == 'POST':
        form = BureauLocalForm(request.POST, instance=bl)
        if form.is_valid():
            form.save()
            messages.success(request, "Bureau Local modifié avec succès.")
            return redirect('bl_liste')
    else:
        form = BureauLocalForm(instance=bl)
    return render(request, 'core/bl_form.html', {
        'form': form, 'titre': f'Modifier {bl.nom}', 'crma': crma
    })


@role_required('sous_superuser')
def bl_supprimer(request, pk):
    crma = request.user.profil.crma
    bl = get_object_or_404(BureauLocal, pk=pk, crma=crma)
    if request.method == 'POST':
        bl.delete()
        messages.success(request, "Bureau Local supprimé.")
        return redirect('bl_liste')
    return render(request, 'core/bl_confirmer_suppression.html', {
        'objet': bl, 'crma': crma
    })

# ─── Gestion des Utilisateurs BL (sous-super-utilisateur CRMA) ───────────────

@role_required('sous_superuser')
def utilisateur_liste(request):
    crma = request.user.profil.crma
    profils = Profil.objects.filter(
        role='utilisateur',
        bureau_local__crma=crma
    ).select_related('user', 'bureau_local')
    return render(request, 'core/utilisateur_liste.html', {
        'profils': profils, 'crma': crma
    })


@role_required('sous_superuser')
def utilisateur_creer(request):
    crma = request.user.profil.crma
    if request.method == 'POST':
        user_form = UserCreationFormCustom(request.POST)
        profil_form = ProfilForm(request.POST)
        profil_form.fields['role'].required = False
        if user_form.is_valid() and profil_form.is_valid():
            # Vérifier que le BL choisi appartient bien à la CRMA
            bl = profil_form.cleaned_data['bureau_local']
            if bl and bl.crma != crma:
                messages.error(request, "Bureau Local invalide.")
                return redirect('utilisateur_liste')
            # Créer le User
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            # Créer le Profil lié
            profil = profil_form.save(commit=False)
            profil.user = user
            profil.role = 'utilisateur'
            profil.save()
            messages.success(request, f"Utilisateur {user.username} créé avec succès.")
            return redirect('utilisateur_liste')
    else:
        user_form = UserCreationFormCustom()
        profil_form = ProfilForm()

    # Limiter les BL proposés à ceux de la CRMA de l'utilisateur connecté
    profil_form.fields['bureau_local'].queryset = BureauLocal.objects.filter(crma=crma)
    profil_form.fields['role'].widget = forms.HiddenInput()
    profil_form.fields['role'].required = False  # ← ajoutez cette ligne

    return render(request, 'core/utilisateur_form.html', {
        'user_form': user_form,
        'profil_form': profil_form,
        'titre': 'Créer un utilisateur',
        'crma': crma
    })


@role_required('sous_superuser')
def utilisateur_modifier(request, pk):
    crma = request.user.profil.crma
    profil = get_object_or_404(
        Profil, pk=pk, role='utilisateur', bureau_local__crma=crma
    )
    if request.method == 'POST':
        user_form = UserModificationForm(request.POST, instance=profil.user)
        profil_form = ProfilForm(request.POST, instance=profil)
        profil_form.fields['role'].required = False
        if user_form.is_valid() and profil_form.is_valid():
            user = user_form.save(commit=False)
            nouveau_mdp = user_form.cleaned_data.get('password1')
            if nouveau_mdp:
                user.set_password(nouveau_mdp)
            user.save()
            profil_form.save()
            messages.success(request, "Utilisateur modifié avec succès.")
            return redirect('utilisateur_liste')
    else:
        user_form = UserModificationForm(instance=profil.user)
        profil_form = ProfilForm(instance=profil)

    profil_form.fields['bureau_local'].queryset = BureauLocal.objects.filter(crma=crma)
    profil_form.fields['role'].widget = forms.HiddenInput()
    profil_form.fields['role'].required = False

    return render(request, 'core/utilisateur_form.html', {
        'user_form': user_form,
        'profil_form': profil_form,
        'titre': f'Modifier {profil.user.get_full_name()}',
        'crma': crma
    })


@role_required('sous_superuser')
def utilisateur_supprimer(request, pk):
    crma = request.user.profil.crma
    profil = get_object_or_404(
        Profil, pk=pk, role='utilisateur', bureau_local__crma=crma
    )
    if request.method == 'POST':
        profil.user.delete()
        messages.success(request, "Utilisateur supprimé.")
        return redirect('utilisateur_liste')
    return render(request, 'core/utilisateur_confirmer_suppression.html', {
        'objet': profil, 'crma': crma
    })