from django import forms
from django.contrib.auth.models import User
from .models import CRMA, BureauLocal, Profil


class CRMAForm(forms.ModelForm):
    class Meta:
        model = CRMA
        fields = [
            'code', 'nom', 'adresse', 'email', 'telephone',
            'ccp_compte', 'ccp_cle', 'badr_compte', 'bna_compte'
        ]
        labels = {
            'code': 'Code CRMA',
            'nom': 'Nom de la CRMA',
            'adresse': 'Adresse',
            'email': 'Email',
            'telephone': 'Téléphone',
            'ccp_compte': 'N° Compte CCP',
            'ccp_cle': 'Clé CCP',
            'badr_compte': 'N° Compte BADR',
            'bna_compte': 'N° Compte BNA',
        }
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'ex: C45'}),
            'nom': forms.TextInput(attrs={'placeholder': 'ex: CRMA de Saïda'}),
            'ccp_compte': forms.TextInput(attrs={'placeholder': 'ex: 380319'}),
            'ccp_cle': forms.TextInput(attrs={'placeholder': 'ex: 50'}),
        }


class BureauLocalForm(forms.ModelForm):
    class Meta:
        model = BureauLocal
        fields = ['code', 'nom', 'adresse']
        labels = {
            'code': 'Code Bureau Local',
            'nom': 'Nom du Bureau Local',
            'adresse': 'Adresse',
        }
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'ex: 279'}),
            'nom': forms.TextInput(attrs={'placeholder': 'ex: BL Saïda Centre'}),
        }


class UserCreationFormCustom(forms.ModelForm):
    """Formulaire de création d'un compte utilisateur."""
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Identifiant',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['role', 'bureau_local', 'poste', 'telephone']
        labels = {
            'role': 'Rôle',
            'bureau_local': 'Bureau Local',
            'poste': 'Poste occupé',
            'telephone': 'Téléphone portable',
        }