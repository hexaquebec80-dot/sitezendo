from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import transaction

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import (
    Commande,
    Facture,
    LigneCommande,
    Notification,
    ParametresEntreprise,
    retirer_stock,
)


@transaction.atomic
def creer_commande_depuis_panier(
    panier,
    client,
    adresse,
    note="",
):
    """
    Crée une commande complète à partir du panier.

    Cette fonction :
    - vérifie que le panier contient des produits;
    - calcule le sous-total;
    - applique le coupon;
    - calcule la TPS et la TVQ;
    - crée la commande;
    - crée les lignes de commande;
    - retire automatiquement le stock;
    - vide le panier;
    - crée une notification;
    - génère la facture PDF.
    """

    lignes_panier = list(
        panier.lignes.select_related(
            "variante__produit",
        )
    )

    if not lignes_panier:
        raise ValueError(
            "Votre panier est vide."
        )

    parametres = (
        ParametresEntreprise.objects.first()
    )

    if parametres is None:
        parametres = (
            ParametresEntreprise.objects.create(
                nom="Zendo Afrique",
                devise="CAD",
                taux_tps=Decimal("5.000"),
                taux_tvq=Decimal("9.975"),
                seuil_stock_faible=5,
            )
        )

    sous_total = panier.sous_total
    remise = panier.remise

    montant_taxable = max(
        Decimal("0.00"),
        sous_total - remise,
    )

    tps = (
        montant_taxable
        * parametres.taux_tps
        / Decimal("100")
    ).quantize(
        Decimal("0.01")
    )

    tvq = (
        montant_taxable
        * parametres.taux_tvq
        / Decimal("100")
    ).quantize(
        Decimal("0.01")
    )

    frais_livraison = Decimal("0.00")

    total = (
        montant_taxable
        + frais_livraison
        + tps
        + tvq
    )

    code_coupon = ""

    if panier.coupon:
        code_coupon = panier.coupon.code

    commande = Commande.objects.create(
        client=client,
        adresse_livraison=adresse,
        statut="attente",
        sous_total=sous_total,
        remise=remise,
        livraison=frais_livraison,
        tps=tps,
        tvq=tvq,
        total=total,
        coupon_code=code_coupon,
        note_client=note,
    )

    for ligne_panier in lignes_panier:
        variante = ligne_panier.variante
        produit = variante.produit

        if ligne_panier.quantite > variante.stock:
            raise ValueError(
                "Stock insuffisant pour "
                f"{produit.nom}. "
                f"Stock disponible : {variante.stock}."
            )

        retirer_stock(
            variante=variante,
            quantite=ligne_panier.quantite,
            reference=commande.numero,
            utilisateur=client,
        )

        details_variante = " / ".join(
            information
            for information in [
                variante.taille,
                variante.couleur,
                variante.modele,
            ]
            if information
        )

        LigneCommande.objects.create(
            commande=commande,
            variante=variante,
            produit_nom=produit.nom,
            sku=variante.sku,
            details_variante=details_variante,
            quantite=ligne_panier.quantite,
            prix_unitaire=ligne_panier.prix_unitaire,
            personnalisation=(
                ligne_panier.personnalisation
            ),
        )

    if panier.coupon:
        coupon = panier.coupon
        coupon.utilisations += 1

        coupon.save(
            update_fields=[
                "utilisations",
            ]
        )

    panier.lignes.all().delete()

    panier.coupon = None

    panier.save(
        update_fields=[
            "coupon",
            "modifie_le",
        ]
    )

    Notification.objects.create(
        utilisateur=client,
        titre="Commande reçue",
        message=(
            "Votre commande "
            f"{commande.numero} "
            "a été créée avec succès."
        ),
        url=(
            "/mon-compte/commandes/"
            f"{commande.pk}/"
        ),
    )

    generer_facture_pdf(
        commande
    )

    return commande


def generer_facture_pdf(commande):
    """
    Génère automatiquement une facture PDF
    pour une commande.
    """

    facture, creation = (
        Facture.objects.get_or_create(
            commande=commande,
        )
    )

    document = BytesIO()

    pdf = canvas.Canvas(
        document,
        pagesize=A4,
    )

    largeur, hauteur = A4

    # En-tête
    pdf.setFont(
        "Helvetica-Bold",
        22,
    )

    pdf.drawString(
        50,
        hauteur - 60,
        "ZENDO AFRIQUE",
    )

    pdf.setFont(
        "Helvetica-Bold",
        14,
    )

    pdf.drawString(
        50,
        hauteur - 95,
        f"FACTURE {facture.numero}",
    )

    # Informations de la commande
    pdf.setFont(
        "Helvetica",
        10,
    )

    pdf.drawString(
        50,
        hauteur - 120,
        f"Commande : {commande.numero}",
    )

    nom_client = (
        commande.client.get_full_name()
        or commande.client.username
    )

    pdf.drawString(
        50,
        hauteur - 137,
        f"Client : {nom_client}",
    )

    pdf.drawString(
        50,
        hauteur - 154,
        f"Courriel : {commande.client.email}",
    )

    adresse = commande.adresse_livraison

    pdf.drawString(
        50,
        hauteur - 171,
        (
            "Livraison : "
            f"{adresse.adresse1}, "
            f"{adresse.ville}, "
            f"{adresse.pays}"
        ),
    )

    # Titres du tableau
    position_y = hauteur - 215

    pdf.setFont(
        "Helvetica-Bold",
        10,
    )

    pdf.drawString(
        50,
        position_y,
        "Produit",
    )

    pdf.drawString(
        330,
        position_y,
        "Quantité",
    )

    pdf.drawRightString(
        largeur - 50,
        position_y,
        "Total",
    )

    position_y -= 12

    pdf.line(
        50,
        position_y,
        largeur - 50,
        position_y,
    )

    position_y -= 20

    # Produits commandés
    pdf.setFont(
        "Helvetica",
        9,
    )

    for ligne in commande.lignes.all():
        nom_produit = ligne.produit_nom

        if ligne.details_variante:
            nom_produit += (
                f" ({ligne.details_variante})"
            )

        pdf.drawString(
            50,
            position_y,
            nom_produit[:55],
        )

        pdf.drawString(
            350,
            position_y,
            str(ligne.quantite),
        )

        pdf.drawRightString(
            largeur - 50,
            position_y,
            f"{ligne.total:.2f} $",
        )

        position_y -= 20

        if position_y < 150:
            pdf.showPage()

            position_y = hauteur - 60

            pdf.setFont(
                "Helvetica",
                9,
            )

    # Totaux
    position_y -= 10

    pdf.line(
        300,
        position_y,
        largeur - 50,
        position_y,
    )

    position_y -= 25

    totaux = [
        (
            "Sous-total",
            commande.sous_total,
        ),
        (
            "Remise",
            -commande.remise,
        ),
        (
            "Livraison",
            commande.livraison,
        ),
        (
            "TPS",
            commande.tps,
        ),
        (
            "TVQ",
            commande.tvq,
        ),
        (
            "TOTAL",
            commande.total,
        ),
    ]

    for titre, montant in totaux:
        if titre == "TOTAL":
            pdf.setFont(
                "Helvetica-Bold",
                11,
            )
        else:
            pdf.setFont(
                "Helvetica",
                10,
            )

        pdf.drawString(
            330,
            position_y,
            titre,
        )

        pdf.drawRightString(
            largeur - 50,
            position_y,
            f"{montant:.2f} $",
        )

        position_y -= 20

    # Pied de page
    pdf.setFont(
        "Helvetica",
        8,
    )

    pdf.drawString(
        50,
        55,
        (
            "Merci d’avoir choisi "
            "Zendo Afrique."
        ),
    )

    pdf.drawString(
        50,
        40,
        (
            "Élégance et créativité "
            "africaine."
        ),
    )

    pdf.save()

    contenu_pdf = document.getvalue()

    document.close()

    nom_fichier = (
        f"{facture.numero}.pdf"
    )

    facture.fichier_pdf.save(
        nom_fichier,
        ContentFile(
            contenu_pdf
        ),
        save=True,
    )

    return facture