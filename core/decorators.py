from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(*roles):
    """
    Décorateur qui vérifie que l'utilisateur connecté
    possède l'un des rôles autorisés.
    Usage : @role_required('superuser') ou @role_required('superuser', 'sous_superuser')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            try:
                profil = request.user.profil
            except Exception:
                return HttpResponseForbidden("Accès refusé : profil introuvable.")

            if profil.role not in roles:
                return HttpResponseForbidden(
                    f"Accès refusé : rôle '{profil.role}' insuffisant."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator