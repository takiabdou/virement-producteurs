import math
from decimal import Decimal, ROUND_HALF_UP


# ─── 1. Calcul des droits Algérie Poste ──────────────────────────────────────

def calculer_droits_poste(montant_jour: Decimal) -> Decimal:
    tranches = math.ceil(float(montant_jour) / 5000)
    droits = Decimal(str(tranches * 12 + 18))
    return droits


def calculer_montant_ccp(montant_jour: Decimal) -> tuple:
    droits = calculer_droits_poste(montant_jour)
    montant_a_verser = montant_jour - droits
    return droits, montant_a_verser


# ─── 2. Génération du numéro de séquence ─────────────────────────────────────

def generer_numero_emission(crma, bureau_local, type_versement, date_versement):
    from .models import BonVersement
    nb_existants = BonVersement.objects.filter(
        bureau_local__crma=crma
    ).count()
    sequence = str(nb_existants + 1).zfill(4)
    date_str = date_versement.strftime('%d%m%Y')
    return f"{crma.code}-{bureau_local.code}-{date_str}/{type_versement}/{sequence}"


# ─── 3. Conversion montant en lettres (français) ─────────────────────────────

UNITES = [
    '', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept',
    'huit', 'neuf', 'dix', 'onze', 'douze', 'treize', 'quatorze',
    'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf'
]

DIZAINES = [
    '', '', 'vingt', 'trente', 'quarante', 'cinquante',
    'soixante', 'soixante', 'quatre-vingt', 'quatre-vingt'
]


def _centaines(n: int) -> str:
    if n == 0:
        return ''
    if n < 20:
        return UNITES[n]
    if n < 100:
        d, u = divmod(n, 10)
        if d == 7:
            if u == 1:
                return f"soixante-et-onze"
            return f"soixante-{UNITES[10 + u]}"
        if d == 9:
            if u == 0:
                return 'quatre-vingt-dix'
            return f"quatre-vingt-dix-{UNITES[u]}"
        if u == 0:
            suffix = 's' if d == 8 else ''
            return f"{DIZAINES[d]}{suffix}"
        if u == 1 and d != 8:
            return f"{DIZAINES[d]}-et-un"
        return f"{DIZAINES[d]}-{UNITES[u]}"
    # Centaines
    c, reste = divmod(n, 100)
    if c == 1:
        prefix = 'cent'
    else:
        prefix = f"{UNITES[c]} cent"
    if reste == 0:
        suffix = 's' if c > 1 else ''
        return f"{prefix}{suffix}"
    return f"{prefix} {_centaines(reste)}"


def montant_en_lettres(montant: Decimal) -> str:
    montant_arrondi = montant.quantize(Decimal('0.01'))
    partie_entiere = int(montant_arrondi)
    centimes = int(round((float(montant_arrondi) - partie_entiere) * 100))

    def convertir(n: int) -> str:
        if n == 0:
            return 'zéro'
        milliards, reste = divmod(n, 1_000_000_000)
        millions, reste = divmod(reste, 1_000_000)
        milliers, cents = divmod(reste, 1000)
        parties = []
        if milliards:
            txt = _centaines(milliards)
            parties.append(f"{txt} milliard{'s' if milliards > 1 else ''}")
        if millions:
            txt = _centaines(millions)
            parties.append(f"{txt} million{'s' if millions > 1 else ''}")
        if milliers:
            if milliers == 1:
                parties.append('mille')
            else:
                parties.append(f"{_centaines(milliers)} mille")
        if cents:
            parties.append(_centaines(cents))
        return ' '.join(parties)

    if partie_entiere == 0:
        resultat = 'zéro dinar'
    else:
        texte = convertir(partie_entiere)
        texte = texte[0].upper() + texte[1:]
        resultat = f"{texte} dinar{'s' if partie_entiere > 1 else ''}"

    if centimes > 0:
        texte_c = convertir(centimes)
        resultat += f" et {texte_c} centime{'s' if centimes > 1 else ''}"

    return resultat