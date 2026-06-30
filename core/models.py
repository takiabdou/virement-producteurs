from django.db import models


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