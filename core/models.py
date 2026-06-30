from django.db import models
from django.contrib.auth.models import User


class CRMA(models.Model):
    code = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    # Coordonnées CCP
    ccp_compte = models.CharField(max_length=20)
    ccp_cle = models.CharField(max_length=5)

    # Coordonnées bancaires
    badr_compte = models.CharField(max_length=30, blank=True)
    bna_compte = models.CharField(max_length=30, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.nom}"

class BureauLocal(models.Model):
    crma = models.ForeignKey(
        CRMA,
        on_delete=models.CASCADE,
        related_name='bureaux_locaux'
    )
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('crma', 'code')

    def __str__(self):
        return f"{self.code} - {self.nom} ({self.crma.code})"


class Profil(models.Model):

    ROLE_CHOICES = [
        ('superuser', 'Super-utilisateur national'),
        ('sous_superuser', 'Sous-super-utilisateur CRMA'),
        ('utilisateur', 'Utilisateur Bureau Local'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='utilisateur'
    )
    bureau_local = models.ForeignKey(
        BureauLocal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs'
    )
    crma = models.ForeignKey(
        CRMA,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_superusers'
    )
    poste = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} [{self.get_role_display()}]"