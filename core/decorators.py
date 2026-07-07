from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('connexion')
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