from django.db.models import Sum

from .models import Panier


def compteur_panier(request):
    """
    Rend le nombre total d’articles du panier disponible
    dans tous les templates avec la variable nombre_panier.
    """

    nombre_panier = 0

    if request.user.is_authenticated:
        panier = (
            Panier.objects.filter(
                client=request.user,
                actif=True,
            )
            .order_by("-pk")
            .first()
        )

    else:
        session_key = request.session.session_key

        if not session_key:
            return {
                "nombre_panier": 0,
            }

        panier = (
            Panier.objects.filter(
                session_key=session_key,
                client__isnull=True,
                actif=True,
            )
            .order_by("-pk")
            .first()
        )

    if panier:
        resultat = panier.lignes.aggregate(
            total=Sum("quantite"),
        )

        nombre_panier = resultat["total"] or 0

    return {
        "nombre_panier": nombre_panier,
    }