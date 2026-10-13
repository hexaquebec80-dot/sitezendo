
from django.contrib import admin, messages
from django.db.models import Count, Sum
from django.utils.html import format_html

from .models import (
    ParametresEntreprise,
    Profil,
    Categorie,
    Tag,
    Produit,
    ImageProduit,
    VarianteProduit,
    MouvementStock,
    Coupon,
    Favori,
    Panier,
    LignePanier,
    Adresse,
    Commande,
    LigneCommande,
    Paiement,
    Facture,
    Livraison,
    Avis,
    Remboursement,
    Notification,
    TicketSupport,
    MessageSupport,
    EvenementCalendrier,
    FAQ,
    DemandePersonnalisation,
)


# ============================================================
# CONFIGURATION GENERALE
# ============================================================

admin.site.site_header = "Zendo Afrique | Administration"
admin.site.site_title = "Zendo Afrique"
admin.site.index_title = "Gestion de la boutique Zendo Afrique"


# ============================================================
# PARAMETRES ENTREPRISE
# ============================================================

@admin.register(ParametresEntreprise)
class ParametresEntrepriseAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "email",
        "telephone",
        "devise",
        "taux_tps",
        "taux_tvq",
    )

    search_fields = ("nom", "email", "telephone")

    readonly_fields = ("cree_le", "modifie_le")

    fieldsets = (
        ("Informations générales", {
            "fields": (
                "nom",
                "slogan",
                "email",
                "telephone",
                "adresse",
                "logo",
            )
        }),
        ("Configuration financière", {
            "fields": (
                "devise",
                "taux_tps",
                "taux_tvq",
                "seuil_stock_faible",
            )
        }),
        ("Historique", {
            "fields": ("cree_le", "modifie_le"),
            "classes": ("collapse",),
        }),
    )


# ============================================================
# PROFILS CLIENTS
# ============================================================

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):

    list_display = (
        "utilisateur",
        "role",
        "telephone",
        "actif",
        "cree_le",
    )

    list_filter = ("role", "actif", "cree_le")

    search_fields = (
        "utilisateur__username",
        "utilisateur__email",
        "utilisateur__first_name",
        "utilisateur__last_name",
        "telephone",
    )

    list_editable = ("role", "actif")

    autocomplete_fields = ("utilisateur",)

    readonly_fields = ("cree_le", "modifie_le")


# ============================================================
# CATEGORIES
# ============================================================

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "parent",
        "active",
        "nombre_produits",
        "apercu_image",
    )

    list_filter = ("active", "parent")

    search_fields = ("nom", "description", "slug")

    prepopulated_fields = {"slug": ("nom",)}

    list_editable = ("active",)

    readonly_fields = ("apercu_image",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            total_produits=Count("produits", distinct=True)
        )

    @admin.display(description="Produits")
    def nombre_produits(self, obj):
        return obj.total_produits

    @admin.display(description="Image")
    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:65px;height:65px;'
                'object-fit:cover;border-radius:8px;" />',
                obj.image.url,
            )
        return "Aucune image"


# ============================================================
# TAGS
# ============================================================

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ("nom", "slug")

    search_fields = ("nom", "slug")

    prepopulated_fields = {"slug": ("nom",)}


# ============================================================
# IMAGES PRODUITS
# ============================================================

class ImageProduitInline(admin.TabularInline):

    model = ImageProduit

    extra = 0

    min_num = 0

    max_num = 20

    fields = (
        "image",
        "texte_alt",
        "principale",
        "ordre",
    )

    verbose_name = "Image facultative"

    verbose_name_plural = "Images du produit (facultatives)"


# ============================================================
# VARIANTES PRODUITS
# ============================================================

class VarianteProduitInline(admin.TabularInline):

    model = VarianteProduit

    extra = 0

    min_num = 0

    fields = (
        "sku",
        "taille",
        "couleur",
        "modele",
        "supplement_prix",
        "stock",
        "seuil_alerte",
        "active",
    )

    verbose_name = "Variante"

    verbose_name_plural = "Variantes du produit"


# ============================================================
# PRODUITS
# ============================================================

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):

    list_display = (
        "apercu_image",
        "nom",
        "sku",
        "categorie",
        "prix",
        "prix_promotionnel",
        "stock_disponible",
        "actif",
        "vedette",
        "personnalisable",
        "cree_le",
    )

    list_display_links = ("nom",)

    list_filter = (
        "actif",
        "vedette",
        "personnalisable",
        "categorie",
        "cree_le",
    )

    search_fields = (
        "nom",
        "sku",
        "description",
        "description_courte",
    )

    list_editable = (
        "actif",
        "vedette",
        "personnalisable",
    )

    prepopulated_fields = {"slug": ("nom",)}

    filter_horizontal = ("tags",)

    autocomplete_fields = ("categorie",)

    readonly_fields = (
        "apercu_image",
        "stock_disponible",
        "cree_le",
        "modifie_le",
    )

    inlines = (
        VarianteProduitInline,
        ImageProduitInline,
    )

    list_per_page = 25

    save_on_top = True

    fieldsets = (
        ("Informations du produit", {
            "fields": (
                "nom",
                "slug",
                "sku",
                "categorie",
                "tags",
                "description_courte",
                "description",
            )
        }),

        ("Prix", {
            "fields": (
                "prix",
                "prix_promotionnel",
                "cout",
            )
        }),

        ("Configuration du produit", {
            "fields": (
                "actif",
                "vedette",
                "personnalisable",
                "delai_personnalisation",
                "poids_kg",
            )
        }),

        ("Aperçu et stock", {
            "fields": (
                "apercu_image",
                "stock_disponible",
            )
        }),

        ("Historique", {
            "fields": (
                "cree_le",
                "modifie_le",
            ),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Image")
    def apercu_image(self, obj):

        if not obj or not obj.pk:
            return "Aucune image"

        image = obj.image_principale

        if image and image.image:
            return format_html(
                '<img src="{}" style="width:65px;height:65px;'
                'object-fit:cover;border-radius:8px;" />',
                image.image.url,
            )

        return "Aucune image"

    @admin.display(description="Stock")
    def stock_disponible(self, obj):

        if not obj or not obj.pk:
            return 0

        return obj.stock_total

    @admin.action(description="Activer les produits sélectionnés")
    def activer_produits(self, request, queryset):
        total = queryset.update(actif=True)
        self.message_user(
            request,
            f"{total} produit(s) activé(s).",
            messages.SUCCESS,
        )

    @admin.action(description="Désactiver les produits sélectionnés")
    def desactiver_produits(self, request, queryset):
        total = queryset.update(actif=False)
        self.message_user(
            request,
            f"{total} produit(s) désactivé(s).",
            messages.SUCCESS,
        )

    @admin.action(description="Mettre les produits en vedette")
    def mettre_en_vedette(self, request, queryset):
        total = queryset.update(vedette=True)
        self.message_user(
            request,
            f"{total} produit(s) en vedette.",
            messages.SUCCESS,
        )

    actions = (
        "activer_produits",
        "desactiver_produits",
        "mettre_en_vedette",
    )


# ============================================================
# IMAGES PRODUITS - GESTION SEPAREE
# ============================================================

@admin.register(ImageProduit)
class ImageProduitAdmin(admin.ModelAdmin):

    list_display = (
        "produit",
        "apercu",
        "principale",
        "ordre",
    )

    list_filter = ("principale",)

    search_fields = (
        "produit__nom",
        "texte_alt",
    )

    autocomplete_fields = ("produit",)

    list_editable = ("ordre",)

    @admin.display(description="Aperçu")
    def apercu(self, obj):

        if obj.image:
            return format_html(
                '<img src="{}" style="width:65px;height:65px;'
                'object-fit:cover;border-radius:8px;" />',
                obj.image.url,
            )

        return "Aucune image"


# ============================================================
# VARIANTES PRODUITS - GESTION SEPAREE
# ============================================================

@admin.register(VarianteProduit)
class VarianteProduitAdmin(admin.ModelAdmin):

    list_display = (
        "produit",
        "sku",
        "taille",
        "couleur",
        "modele",
        "stock",
        "seuil_alerte",
        "stock_faible",
        "active",
    )

    list_filter = ("active", "produit")

    search_fields = (
        "sku",
        "produit__nom",
        "taille",
        "couleur",
        "modele",
    )

    autocomplete_fields = ("produit",)

    list_editable = ("stock", "active")

    readonly_fields = ("cree_le", "modifie_le")


# ============================================================
# MOUVEMENTS STOCK
# ============================================================

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):

    list_display = (
        "variante",
        "type_mouvement",
        "quantite",
        "stock_apres",
        "reference",
        "utilisateur",
        "cree_le",
    )

    list_filter = (
        "type_mouvement",
        "cree_le",
    )

    search_fields = (
        "variante__sku",
        "reference",
        "note",
    )

    autocomplete_fields = (
        "variante",
        "utilisateur",
    )

    readonly_fields = (
        "cree_le",
        "modifie_le",
    )


# ============================================================
# COUPONS PROMOTIONNELS
# ============================================================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "type_remise",
        "valeur",
        "minimum_commande",
        "debut",
        "fin",
        "utilisations",
        "limite_utilisations",
        "actif",
    )

    list_filter = (
        "type_remise",
        "actif",
    )

    search_fields = ("code",)

    list_editable = ("actif",)


# ============================================================
# FAVORIS
# ============================================================

@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):

    list_display = (
        "client",
        "produit",
        "cree_le",
    )

    search_fields = (
        "client__username",
        "produit__nom",
    )

    autocomplete_fields = (
        "client",
        "produit",
    )


# ============================================================
# PANIER
# ============================================================

class LignePanierInline(admin.TabularInline):

    model = LignePanier

    extra = 0

    autocomplete_fields = ("variante",)

    fields = (
        "variante",
        "quantite",
        "personnalisation",
        "fichier_personnalisation",
    )


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "client",
        "session_key",
        "coupon",
        "actif",
        "total_panier",
        "cree_le",
    )

    list_filter = ("actif", "cree_le")

    search_fields = (
        "client__username",
        "session_key",
    )

    autocomplete_fields = ("client", "coupon")

    inlines = (LignePanierInline,)

    readonly_fields = ("cree_le", "modifie_le")

    @admin.display(description="Total")
    def total_panier(self, obj):
        return f"{obj.total:.2f} $"


@admin.register(LignePanier)
class LignePanierAdmin(admin.ModelAdmin):

    list_display = (
        "panier",
        "variante",
        "quantite",
        "total_ligne",
    )

    autocomplete_fields = ("variante",)

    @admin.display(description="Total")
    def total_ligne(self, obj):
        return f"{obj.total:.2f} $"


# ============================================================
# ADRESSES CLIENTS
# ============================================================

@admin.register(Adresse)
class AdresseAdmin(admin.ModelAdmin):

    list_display = (
        "nom_complet",
        "client",
        "telephone",
        "ville",
        "province",
        "pays",
        "principale",
    )

    list_filter = ("pays", "principale")

    search_fields = (
        "nom_complet",
        "telephone",
        "ville",
        "code_postal",
        "client__username",
    )

    autocomplete_fields = ("client",)


# ============================================================
# LIGNES COMMANDES
# ============================================================

class LigneCommandeInline(admin.TabularInline):

    model = LigneCommande

    extra = 0

    fields = (
        "produit_nom",
        "sku",
        "details_variante",
        "quantite",
        "prix_unitaire",
        "personnalisation",
    )


# ============================================================
# PAIEMENTS EN LIGNE
# ============================================================

class PaiementInline(admin.TabularInline):

    model = Paiement

    extra = 0

    fields = (
        "methode",
        "statut",
        "montant",
        "reference_externe",
        "paye_le",
    )


# ============================================================
# SUIVI LIVRAISON
# ============================================================

class LivraisonInline(admin.StackedInline):

    model = Livraison

    extra = 0

    max_num = 1

    can_delete = False

    fields = (
        "transporteur",
        "numero_suivi",
        "url_suivi",
        "statut",
        "date_expedition",
        "livraison_prevue",
    )


# ============================================================
# COMMANDES
# ============================================================

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "client",
        "statut_colore",
        "total",
        "livraison",
        "nombre_relances_paiement",
        "cree_le",
    )

    list_filter = (
        "statut",
        "cree_le",
    )

    search_fields = (
        "numero",
        "client__username",
        "client__email",
        "coupon_code",
    )

    autocomplete_fields = (
        "client",
        "adresse_livraison",
    )

    readonly_fields = (
        "numero",
        "cree_le",
        "modifie_le",
        "derniere_relance_paiement",
        "nombre_relances_paiement",
    )

    inlines = (
        LigneCommandeInline,
        PaiementInline,
        LivraisonInline,
    )

    list_per_page = 30

    save_on_top = True

    fieldsets = (
        ("Commande", {
            "fields": (
                "numero",
                "client",
                "statut",
                "adresse_livraison",
            )
        }),

        ("Montants", {
            "fields": (
                "sous_total",
                "remise",
                "livraison",
                "tps",
                "tvq",
                "total",
                "coupon_code",
            )
        }),

        ("Informations du client", {
            "fields": ("note_client",)
        }),

        ("Relances de paiement", {
            "fields": (
                "derniere_relance_paiement",
                "nombre_relances_paiement",
            )
        }),

        ("Historique", {
            "fields": (
                "cree_le",
                "modifie_le",
            ),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Statut", ordering="statut")
    def statut_colore(self, obj):

        couleurs = {
            "brouillon": "#64748b",
            "attente": "#f59e0b",
            "confirmee": "#2563eb",
            "preparation": "#8b5cf6",
            "expediee": "#0891b2",
            "livree": "#16a34a",
            "annulee": "#dc2626",
            "remboursee": "#475569",
        }

        couleur = couleurs.get(obj.statut, "#64748b")

        return format_html(
            '<span style="background:{};color:white;'
            'padding:5px 10px;border-radius:20px;">{}</span>',
            couleur,
            obj.get_statut_display(),
        )

    @admin.action(description="Marquer comme confirmées")
    def confirmer_commandes(self, request, queryset):
        total = queryset.update(statut="confirmee")
        self.message_user(
            request,
            f"{total} commande(s) confirmée(s).",
        )

    @admin.action(description="Marquer en préparation")
    def preparer_commandes(self, request, queryset):
        total = queryset.update(statut="preparation")
        self.message_user(
            request,
            f"{total} commande(s) en préparation.",
        )

    @admin.action(description="Marquer comme expédiées")
    def expedier_commandes(self, request, queryset):
        total = queryset.update(statut="expediee")
        self.message_user(
            request,
            f"{total} commande(s) expédiée(s).",
        )

    @admin.action(description="Marquer comme livrées")
    def livrer_commandes(self, request, queryset):
        total = queryset.update(statut="livree")
        self.message_user(
            request,
            f"{total} commande(s) livrée(s).",
        )

    actions = (
        "confirmer_commandes",
        "preparer_commandes",
        "expedier_commandes",
        "livrer_commandes",
    )


@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):

    list_display = (
        "commande",
        "produit_nom",
        "sku",
        "quantite",
        "prix_unitaire",
        "total_ligne",
    )

    search_fields = (
        "commande__numero",
        "produit_nom",
        "sku",
    )

    @admin.display(description="Total")
    def total_ligne(self, obj):
        return f"{obj.total:.2f} $"


# ============================================================
# PAIEMENTS
# ============================================================

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):

    list_display = (
        "commande",
        "methode",
        "statut",
        "montant",
        "reference_externe",
        "paye_le",
        "cree_le",
    )

    list_filter = (
        "methode",
        "statut",
        "cree_le",
    )

    search_fields = (
        "commande__numero",
        "reference_externe",
    )

    autocomplete_fields = ("commande",)

    readonly_fields = (
        "cree_le",
        "modifie_le",
    )


# ============================================================
# FACTURES
# ============================================================

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "commande",
        "envoyee",
        "telecharger_pdf",
        "cree_le",
    )

    list_filter = ("envoyee", "cree_le")

    search_fields = (
        "numero",
        "commande__numero",
    )

    autocomplete_fields = ("commande",)

    readonly_fields = ("numero", "cree_le", "modifie_le")

    @admin.display(description="PDF")
    def telecharger_pdf(self, obj):

        if obj.fichier_pdf:
            return format_html(
                '<a href="{}" target="_blank" '
                'rel="noopener noreferrer">Télécharger</a>',
                obj.fichier_pdf.url,
            )

        return "Non disponible"


# ============================================================
# LIVRAISONS
# ============================================================

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):

    list_display = (
        "commande",
        "transporteur",
        "numero_suivi",
        "statut",
        "date_expedition",
        "livraison_prevue",
    )

    list_filter = ("statut", "transporteur")

    search_fields = (
        "commande__numero",
        "numero_suivi",
        "transporteur",
    )

    autocomplete_fields = ("commande",)

    list_editable = ("statut",)


# ============================================================
# AVIS CLIENTS
# ============================================================

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):

    list_display = (
        "produit",
        "client",
        "note",
        "titre",
        "approuve",
        "cree_le",
    )

    list_filter = (
        "note",
        "approuve",
        "cree_le",
    )

    search_fields = (
        "produit__nom",
        "client__username",
        "titre",
        "commentaire",
    )

    autocomplete_fields = ("produit", "client")

    list_editable = ("approuve",)

    @admin.action(description="Approuver les avis")
    def approuver_avis(self, request, queryset):
        total = queryset.update(approuve=True)
        self.message_user(
            request,
            f"{total} avis approuvé(s).",
        )

    actions = ("approuver_avis",)


# ============================================================
# REMBOURSEMENTS
# ============================================================

@admin.register(Remboursement)
class RemboursementAdmin(admin.ModelAdmin):

    list_display = (
        "paiement",
        "montant",
        "statut",
        "cree_le",
    )

    list_filter = ("statut",)

    search_fields = (
        "paiement__commande__numero",
        "motif",
    )

    autocomplete_fields = ("paiement",)


# ============================================================
# NOTIFICATIONS
# ============================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "utilisateur",
        "titre",
        "lue",
        "cree_le",
    )

    list_filter = ("lue", "cree_le")

    search_fields = (
        "utilisateur__username",
        "titre",
        "message",
    )

    autocomplete_fields = ("utilisateur",)

    list_editable = ("lue",)


# ============================================================
# SUPPORT CLIENT
# ============================================================

class MessageSupportInline(admin.TabularInline):

    model = MessageSupport

    extra = 0

    autocomplete_fields = ("auteur",)


@admin.register(TicketSupport)
class TicketSupportAdmin(admin.ModelAdmin):

    list_display = (
        "sujet",
        "client",
        "statut",
        "assigne_a",
        "cree_le",
    )

    list_filter = (
        "statut",
        "cree_le",
    )

    search_fields = (
        "sujet",
        "client__username",
        "message",
    )

    autocomplete_fields = (
        "client",
        "assigne_a",
    )

    inlines = (MessageSupportInline,)

    list_editable = ("statut",)


@admin.register(MessageSupport)
class MessageSupportAdmin(admin.ModelAdmin):

    list_display = (
        "ticket",
        "auteur",
        "cree_le",
    )

    search_fields = (
        "ticket__sujet",
        "auteur__username",
        "contenu",
    )

    autocomplete_fields = (
        "ticket",
        "auteur",
    )


# ============================================================
# CALENDRIER
# ============================================================

@admin.register(EvenementCalendrier)
class EvenementCalendrierAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "type_evenement",
        "debut",
        "fin",
        "termine",
    )

    list_filter = (
        "type_evenement",
        "termine",
    )

    search_fields = (
        "titre",
        "description",
    )

    filter_horizontal = ("assigne_a",)

    list_editable = ("termine",)


# ============================================================
# FAQ
# ============================================================

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):

    list_display = (
        "question",
        "ordre",
        "publiee",
    )

    search_fields = (
        "question",
        "reponse",
    )

    list_editable = ("ordre", "publiee")


# ============================================================
# DEMANDES DE PERSONNALISATION
# ============================================================

@admin.register(DemandePersonnalisation)
class DemandePersonnalisationAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "nom_entreprise",
        "type_client",
        "telephone",
        "email",
        "quantite",
        "statut",
        "cree_le",
    )

    list_filter = (
        "type_client",
        "statut",
        "cree_le",
    )

    search_fields = (
        "nom",
        "nom_entreprise",
        "telephone",
        "email",
        "code_postal",
    )

    list_editable = ("statut",)

    readonly_fields = ("cree_le",)

    list_per_page = 30

    save_on_top = True

    fieldsets = (
        ("Informations du client", {
            "fields": (
                "type_client",
                "nom",
                "nom_entreprise",
                "telephone",
                "email",
                "code_postal",
            )
        }),

        ("Personnalisation demandée", {
            "fields": (
                "quantite",
                "couleur",
                "taille",
                "description",
                "fichier",
            )
        }),

        ("Suivi", {
            "fields": (
                "statut",
                "cree_le",
            )
        }),
    )

    @admin.action(description="Marquer en traitement")
    def marquer_traitement(self, request, queryset):
        total = queryset.update(statut="traitement")
        self.message_user(
            request,
            f"{total} demande(s) en traitement.",
        )

    @admin.action(description="Marquer comme terminées")
    def marquer_terminees(self, request, queryset):
        total = queryset.update(statut="terminee")
        self.message_user(
            request,
            f"{total} demande(s) terminée(s).",
        )

    actions = (
        "marquer_traitement",
        "marquer_terminees",
    )
