from django.contrib import admin
from .models import CRMA, BureauLocal, Profil


@admin.register(CRMA)
class CRMAAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'ccp_compte', 'ccp_cle', 'email')
    search_fields = ('code', 'nom')

@admin.register(BureauLocal)
class BureauLocalAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'crma')
    list_filter = ('crma',)
    search_fields = ('code', 'nom')

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'crma', 'bureau_local', 'poste')
    list_filter = ('role', 'crma')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')