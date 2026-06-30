from django.contrib import admin
from .models import CRMA, BureauLocal


@admin.register(CRMA)
class CRMAAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'ccp_compte', 'ccp_cle', 'email')
    search_fields = ('code', 'nom')

@admin.register(BureauLocal)
class BureauLocalAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'crma')
    list_filter = ('crma',)
    search_fields = ('code', 'nom')