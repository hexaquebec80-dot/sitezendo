
from django.shortcuts import render
from .models import ControleBoutique


class ControleBoutiqueMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        chemin = request.path_info

        # L'administration reste accessible pour
        # permettre à HexaQuébec de réactiver le site.
        if chemin.startswith("/admin/"):
            return self.get_response(request)

        # Ne pas intercepter les fichiers statiques.
        if chemin.startswith("/static/"):
            return self.get_response(request)

        controle = ControleBoutique.objects.filter(
            pk=1
        ).first()

        if controle:

            if controle.est_fermee:
                return render(
                    request,
                    "zendo/boutique_fermee.html",
                    status=410
                )

            if controle.est_suspendue:
                return render(
                    request,
                    "zendo/boutique_suspendue.html",
                    status=503
                )

        return self.get_response(request)
