from django.urls import path

from . import views


app_name = "zendo"


urlpatterns = [
    # Page d’accueil
    path(
        "",
        views.accueil,
        name="accueil",
    ),

    # Catalogue
    path(
        "boutique/",
        views.catalogue,
        name="catalogue",
    ),

    path(
        "categorie/<slug:slug>/",
        views.catalogue,
        name="categorie",
    ),

    # Produits
    path(
        "produit/<slug:slug>/",
        views.produit_detail,
        name="produit_detail",
    ),

    path(
        "produit/<slug:slug>/ajouter/",
        views.ajouter_panier,
        name="ajouter_panier",
    ),

    path(
        "produit/<slug:slug>/avis/",
        views.ajouter_avis,
        name="ajouter_avis",
    ),

    # Favoris
    path(
        "favori/<int:pk>/",
        views.favori_basculer,
        name="favori",
    ),

    # Panier
    path(
        "panier/",
        views.panier,
        name="panier",
    ),

    path(
        "panier/ligne/<int:pk>/",
        views.modifier_ligne,
        name="modifier_ligne",
    ),

    path(
        "panier/coupon/",
        views.appliquer_coupon,
        name="appliquer_coupon",
    ),

    # Commande
    path(
        "commande/",
        views.checkout,
        name="checkout",
    ),

    # Inscription et connexion
    path(
        "inscription/",
        views.inscription,
        name="inscription",
    ),

    path(
        "connexion/",
        views.ConnexionView.as_view(),
        name="connexion",
    ),

    path(
        "deconnexion/",
        views.DeconnexionView.as_view(),
        name="deconnexion",
    ),

    # Compte client
    path(
        "mon-compte/",
        views.compte,
        name="compte",
    ),

    path(
        "mon-compte/commandes/<int:pk>/",
        views.commande_detail,
        name="commande_detail",
    ),

    # Factures PDF
    path(
        "factures/<int:pk>/pdf/",
        views.facture_pdf,
        name="facture_pdf",
    ),

    # Support
    path(
        "support/",
        views.support,
        name="support",
    ),

    # FAQ
    path(
        "faq/",
        views.faq,
        name="faq",
    ),

    # Tableau de bord professionnel
    path(
        "gestion/",
        views.tableau_bord,
        name="tableau_bord",
    ),


    path(
        "gestion/produits/ajouter/",
        views.produit_ajouter,
        name="produit_ajouter",
    ),

    path(
        "gestion/produits/<int:pk>/modifier/",
        views.produit_modifier,
        name="produit_modifier",
    ),

    path(
        "gestion/produits/<int:pk>/supprimer/",
        views.produit_supprimer,
        name="produit_supprimer",
    ),

    path(
        "gestion/livraisons/ajouter/",
        views.livraison_ajouter,
        name="livraison_ajouter",
    ),

    path(
        "gestion/livraisons/<int:pk>/modifier/",
        views.livraison_modifier,
        name="livraison_modifier",
    ),
    path(
    "gestion/produits/<int:pk>/modifier/",
    views.produit_modifier,
    name="produit_modifier",
    ),
    path(
    "commande/<int:pk>/payer/stripe/",
    views.payer_commande_stripe,
    name="payer_commande_stripe",
    ),

    path(
    "stripe/webhook/",
    views.stripe_webhook,
    name="stripe_webhook",
    ),
   path(
    "diam-ia/chat/",
    views.diam_ia_chat,
    name="diam_ia_chat",
    ),

    path(
    "gestion/commandes/",
    views.gestion_commandes,
    name="gestion_commandes",
),

path(
    "gestion/commandes/<int:pk>/",
    views.gestion_commande_detail,
    name="gestion_commande_detail",
),

path(
    "gestion/commandes/<int:pk>/relance-paiement/",
    views.relancer_paiement_commande,
    name="relancer_paiement_commande",
),

path(
    "gestion/clients/",
    views.gestion_clients,
    name="gestion_clients",
),

path(
    "gestion/clients/<int:pk>/",
    views.gestion_client_detail,
    name="gestion_client_detail",
),
path(
    "favori/<int:pk>/",
    views.favori_basculer,
    name="favori_basculer",
),

path(
    "produit/<slug:slug>/avis/",
    views.ajouter_avis,
    name="ajouter_avis",
),
path(
    "api/recherche-produits/",
    views.recherche_produits_api,
    name="recherche_produits_api",
),

path(
    "personnalisation/",
    views.demande_personnalisation,
    name="demande_personnalisation",
),

path(
    "personnalisation/succes/",
    views.demande_personnalisation_succes,
    name="demande_personnalisation_succes",
),

]