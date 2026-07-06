from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CRMAForm, BureauLocalForm, UserCreationFormCustom, UserModificationForm, ProfilForm
from .decorators import role_required
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone
from .models import CRMA, BureauLocal, Profil, LigneEncaissement, BonVersement
from decimal import Decimal
import datetime
from .calculs import calculer_montant_ccp, montant_en_lettres, generer_numero_emission

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

@role_required('utilisateur')
def brouillard(request):
    bl = request.user.profil.bureau_local
    aujourd_hui = datetime.date.today()

    # Permet de consulter un jour précédent via ?date=YYYY-MM-DD
    date_str = request.GET.get('date')
    if date_str:
        try:
            date_selectionnee = datetime.date.fromisoformat(date_str)
        except ValueError:
            date_selectionnee = aujourd_hui
    else:
        date_selectionnee = aujourd_hui

    est_aujourd_hui = (date_selectionnee == aujourd_hui)

    lignes = LigneEncaissement.objects.filter(
        bureau_local=bl,
        date=date_selectionnee
    )
    total_jour = sum(l.montant for l in lignes) if lignes else Decimal('0')

    # Liste des jours ayant des encaissements (pour le sélecteur)
    jours_disponibles = LigneEncaissement.objects.filter(
        bureau_local=bl
    ).values_list('date', flat=True).distinct().order_by('-date')

    return render(request, 'core/brouillard.html', {
        'bl': bl,
        'lignes': lignes,
        'total_jour': total_jour,
        'aujourd_hui': aujourd_hui,
        'date_selectionnee': date_selectionnee,
        'est_aujourd_hui': est_aujourd_hui,
        'jours_disponibles': jours_disponibles,
    })


@role_required('utilisateur')
def encaissement_ajouter(request):
    """Saisie d'un nouvel encaissement."""
    bl = request.user.profil.bureau_local
    if request.method == 'POST':
        montant_str = request.POST.get('montant', '').replace(',', '.')
        numero_contrat = request.POST.get('numero_contrat', '').strip()
        try:
            montant = Decimal(montant_str)
            if montant <= 0:
                raise ValueError
        except Exception:
            messages.error(request, "Montant invalide. Saisissez un nombre positif.")
            return redirect('brouillard')

        LigneEncaissement.objects.create(
            bureau_local=bl,
            saisi_par=request.user,
            montant=montant,
            numero_contrat=numero_contrat
        )
        messages.success(request, f"Encaissement de {montant:,.2f} DA enregistré.")
        return redirect('brouillard')

    return redirect('brouillard')


@role_required('utilisateur')
def encaissement_supprimer(request, pk):
    """Suppression d'une ligne d'encaissement de la journée en cours."""
    bl = request.user.profil.bureau_local
    aujourd_hui = timezone.localdate()
    ligne = get_object_or_404(
        LigneEncaissement, pk=pk, bureau_local=bl, date=aujourd_hui
    )
    if request.method == 'POST':
        ligne.delete()
        messages.success(request, "Ligne supprimée.")
    return redirect('brouillard')

@role_required('utilisateur')
def choisir_versement(request):
    """Page de choix du mode de versement et confirmation du montant."""
    bl = request.user.profil.bureau_local
    crma = bl.crma
    aujourd_hui = datetime.date.today()

    # Récupérer le total du jour
    lignes = LigneEncaissement.objects.filter(
        bureau_local=bl,
        date=aujourd_hui
    )
    total_jour = sum(l.montant for l in lignes) if lignes else Decimal('0')

    if total_jour == 0:
        messages.error(request, "Aucun encaissement saisi aujourd'hui.")
        return redirect('brouillard')

    # Calculer les montants pour chaque mode
    droits_ccp, net_ccp = calculer_montant_ccp(total_jour)

    context = {
        'bl': bl,
        'crma': crma,
        'aujourd_hui': aujourd_hui,
        'total_jour': total_jour,
        'droits_ccp': droits_ccp,
        'net_ccp': net_ccp,
        'net_banque': total_jour,  # Pas de déduction pour BADR/BNA
    }
    return render(request, 'core/choisir_versement.html', context)


@role_required('utilisateur')
def apercu_versement(request):
    """Génère et affiche le bon de versement selon le mode choisi."""
    if request.method != 'POST':
        return redirect('brouillard')

    bl = request.user.profil.bureau_local
    crma = bl.crma
    aujourd_hui = datetime.date.today()
    type_versement = request.POST.get('type_versement')

    if type_versement not in ('CCP', 'BADR', 'BNA'):
        messages.error(request, "Mode de versement invalide.")
        return redirect('choisir_versement')

    # Récupérer le total du jour
    lignes = LigneEncaissement.objects.filter(
        bureau_local=bl,
        date=aujourd_hui
    )
    total_jour = sum(l.montant for l in lignes) if lignes else Decimal('0')

    # Calculer selon le mode
    if type_versement == 'CCP':
        droits, montant_a_verser = calculer_montant_ccp(total_jour)
    else:
        droits = Decimal('0')
        montant_a_verser = total_jour

    # Générer le numéro d'émission
    numero = generer_numero_emission(crma, bl, type_versement, aujourd_hui)

    # Montant en lettres
    montant_lettres = montant_en_lettres(montant_a_verser)

    # Créer le bon en base
    bon = BonVersement.objects.create(
        bureau_local=bl,
        emis_par=request.user,
        type_versement=type_versement,
        numero_emission=numero,
        montant_jour=total_jour,
        droits_poste=droits,
        montant_a_verser=montant_a_verser,
        date_versement=aujourd_hui,
    )

    context = {
        'bon': bon,
        'bl': bl,
        'crma': crma,
        'user': request.user,
        'montant_lettres': montant_lettres,
        'aujourd_hui': aujourd_hui,
        'type_versement': type_versement,
    }

    if type_versement == 'CCP':
        return render(request, 'core/bon_ccp.html', context)
    else:
        return render(request, 'core/bon_bancaire.html', context)

 # ─── Historique des bons de versement ────────────────────────────────────────

@login_required
def historique_bons(request):
    """
    Historique des bons selon le rôle de l'utilisateur connecté.
    """
    try:
        role = request.user.profil.role
    except Exception:
        return redirect('connexion')

    if role == 'utilisateur':
        bons = BonVersement.objects.filter(
            bureau_local=request.user.profil.bureau_local
        )
    elif role == 'sous_superuser':
        bons = BonVersement.objects.filter(
            bureau_local__crma=request.user.profil.crma
        )
    else:  # superuser
        bons = BonVersement.objects.all()

    # Filtres optionnels par date
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    type_filtre = request.GET.get('type_versement')

    if date_debut:
        bons = bons.filter(date_emission__gte=date_debut)
    if date_fin:
        bons = bons.filter(date_emission__lte=date_fin)
    if type_filtre and type_filtre in ('CCP', 'BADR', 'BNA'):
        bons = bons.filter(type_versement=type_filtre)

    bons = bons.select_related(
        'bureau_local', 'bureau_local__crma', 'emis_par'
    ).order_by('-date_emission', '-id')

    total_periode = sum(b.montant_a_verser for b in bons)

    return render(request, 'core/historique_bons.html', {
        'bons': bons,
        'total_periode': total_periode,
        'date_debut': date_debut or '',
        'date_fin': date_fin or '',
        'type_filtre': type_filtre or '',
    })


@login_required
def reimprimer_bon(request, pk):
    """Réimprime un bon existant sans en créer un nouveau."""
    try:
        role = request.user.profil.role
    except Exception:
        return redirect('connexion')

    # Filtrer selon le rôle
    if role == 'utilisateur':
        bon = get_object_or_404(
            BonVersement, pk=pk,
            bureau_local=request.user.profil.bureau_local
        )
    elif role == 'sous_superuser':
        bon = get_object_or_404(
            BonVersement, pk=pk,
            bureau_local__crma=request.user.profil.crma
        )
    else:
        bon = get_object_or_404(BonVersement, pk=pk)

    bl = bon.bureau_local
    crma = bl.crma
    montant_lettres = montant_en_lettres(bon.montant_a_verser)

    context = {
        'bon': bon,
        'bl': bl,
        'crma': crma,
        'user': bon.emis_par,
        'montant_lettres': montant_lettres,
        'aujourd_hui': bon.date_versement,
        'type_versement': bon.type_versement,
        'reimprimer': True,
    }

    if bon.type_versement == 'CCP':
        return render(request, 'core/bon_ccp.html', context)
    else:
        return render(request, 'core/bon_bancaire.html', context)