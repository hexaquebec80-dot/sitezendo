from django.contrib import admin
from .models import *

admin.site.site_header = "Zendo Afrique — Administration"
admin.site.site_title = "Zendo Afrique"
admin.site.index_title = "Gestion du commerce"

class ImageProduitInline(admin.TabularInline): model = ImageProduit; extra = 1
class VarianteInline(admin.TabularInline): model = VarianteProduit; extra = 1


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("nom", "sku", "categorie", "prix", "prix_promotionnel", "stock_total", "actif", "vedette", "personnalisable")
    list_filter = ("actif", "vedette", "personnalisable", "categorie", "tags")
    search_fields = ("nom", "sku", "description")
    prepopulated_fields = {"slug": ("nom",)}
    filter_horizontal = ("tags",)
    inlines = (ImageProduitInline, VarianteInline)

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "parent", "active"); list_filter = ("active",); search_fields = ("nom",); prepopulated_fields = {"slug": ("nom",)}
@admin.register(VarianteProduit)
class VarianteAdmin(admin.ModelAdmin):
    list_display = ("sku", "produit", "taille", "couleur", "modele", "stock", "stock_faible", "active")
    list_filter = ("active", "taille", "couleur"); search_fields = ("sku", "produit__nom")
@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ("variante", "type_mouvement", "quantite", "stock_apres", "reference", "cree_le")
    list_filter = ("type_mouvement", "cree_le"); search_fields = ("variante__sku", "reference"); readonly_fields = ("cree_le", "modifie_le")
class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

    readonly_fields = (
        "produit_nom",
        "sku",
        "quantite",
        "prix_unitaire",
    )


class PaiementInline(admin.TabularInline):
    model = Paiement
    extra = 0


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "client",
        "statut",
        "total",
        "statut_paiement",
        "nombre_relances_paiement",
        "derniere_relance_paiement",
        "cree_le",
    )

    list_filter = (
        "statut",
        "cree_le",
    )

    search_fields = (
        "numero",
        "client__username",
        "client__first_name",
        "client__last_name",
        "client__email",
    )

    inlines = (
        LigneCommandeInline,
        PaiementInline,
    )

    readonly_fields = (
        "numero",
        "nombre_relances_paiement",
        "derniere_relance_paiement",
    )

    ordering = (
        "-cree_le",
    )


    @admin.display(description="Paiement")
    def statut_paiement(self, obj):

        if obj.paiements.filter(statut="paye").exists():
            return "✅ Payé"

        if obj.paiements.filter(statut="autorise").exists():
            return "🟡 Autorisé"

        if obj.paiements.filter(statut="echoue").exists():
            return "❌ Échoué"

        if obj.paiements.filter(statut="rembourse").exists():
            return "↩️ Remboursé"

        return "⏳ En attente"
    
@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("commande", "methode", "statut", "montant", "reference_externe", "cree_le")
    list_filter = ("methode", "statut"); search_fields = ("commande__numero", "reference_externe")
@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin): list_display = ("numero", "commande", "envoyee", "cree_le"); search_fields = ("numero", "commande__numero")
@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin): list_display = ("commande", "transporteur", "numero_suivi", "statut", "livraison_prevue"); list_filter = ("statut", "transporteur")
@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin): list_display = ("produit", "client", "note", "approuve", "cree_le"); list_filter = ("note", "approuve"); list_editable = ("approuve",)
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin): list_display = ("code", "type_remise", "valeur", "debut", "fin", "utilisations", "actif"); list_filter = ("type_remise", "actif")
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin): list_display = ("utilisateur", "role", "telephone", "actif"); list_filter = ("role", "actif"); search_fields = ("utilisateur__username", "utilisateur__email")
@admin.register(TicketSupport)
class TicketAdmin(admin.ModelAdmin): list_display = ("sujet", "client", "statut", "assigne_a", "cree_le"); list_filter = ("statut",); search_fields = ("sujet", "client__email")

for model in [ParametresEntreprise, Tag, Favori, Panier, LignePanier, Adresse, Remboursement, Notification, MessageSupport, EvenementCalendrier, FAQ]:
    try: admin.site.register(model)
    except admin.sites.AlreadyRegistered: pass





from django.contrib import admin

from .models import DemandePersonnalisation


@admin.register(DemandePersonnalisation)
class DemandePersonnalisationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
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
        "description",
    )

    readonly_fields = (
        "cree_le",
    )

    list_per_page = 25

    ordering = (
        "-cree_le",
    )

    fieldsets = (

        (
            "Client",
            {
                "fields": (
                    "type_client",
                    "nom",
                    "nom_entreprise",
                    "telephone",
                    "email",
                    "code_postal",
                )
            },
        ),

        (
            "Demande de personnalisation",
            {
                "fields": (
                    "quantite",
                    "couleur",
                    "taille",
                    "description",
                    "fichier",
                )
            },
        ),

        (
            "Suivi de la demande",
            {
                "fields": (
                    "statut",
                    "cree_le",
                )
            },
        ),

    )