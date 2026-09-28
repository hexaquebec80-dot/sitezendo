from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

class TimeStampedModel(models.Model):
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    class Meta: abstract = True

class ParametresEntreprise(TimeStampedModel):
    nom = models.CharField(max_length=150, default="Zendo Afrique")
    slogan = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    adresse = models.TextField(blank=True)
    devise = models.CharField(max_length=3, default="CAD")
    taux_tps = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("5.000"))
    taux_tvq = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("9.975"))
    seuil_stock_faible = models.PositiveIntegerField(default=5)
    logo = models.ImageField(upload_to="logos/", blank=True)
    class Meta: verbose_name_plural = "Paramètres de l’entreprise"
    def __str__(self): return self.nom

class Profil(TimeStampedModel):
    ROLES = [("client", "Client"), ("employe", "Employé"), ("gestionnaire", "Gestionnaire"), ("admin", "Administrateur")]
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil_zendo")
    role = models.CharField(max_length=20, choices=ROLES, default="client")
    telephone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to="profils/", blank=True)
    actif = models.BooleanField(default=True)
    def __str__(self): return f"{self.utilisateur.get_full_name() or self.utilisateur.username} — {self.get_role_display()}"



class Categorie(TimeStampedModel):

    nom = models.CharField(
        max_length=120
    )

    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sous_categories"
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True
    )

    active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["nom"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.nom)

            slug = base_slug

            numero = 2

            while Categorie.objects.exclude(
                pk=self.pk
            ).filter(
                slug=slug
            ).exists():

                slug = f"{base_slug}-{numero}"

                numero += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):

        if self.parent:

            return f"{self.parent.nom} → {self.nom}"

        return self.nom

class Tag(models.Model):
    nom = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    def __str__(self): return self.nom

class Produit(TimeStampedModel):
    nom = models.CharField(max_length=180)
    slug = models.SlugField(max_length=210, unique=True, blank=True)
    sku = models.CharField(max_length=60, unique=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="produits")
    tags = models.ManyToManyField(Tag, blank=True, related_name="produits")
    description_courte = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    prix = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    prix_promotionnel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cout = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actif = models.BooleanField(default=True)
    vedette = models.BooleanField(default=False)
    personnalisable = models.BooleanField(default=False)
    delai_personnalisation = models.PositiveIntegerField(default=0, help_text="Nombre de jours")
    poids_kg = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    class Meta: ordering = ["-cree_le"]
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nom); candidate = base; n = 2
            while Produit.objects.exclude(pk=self.pk).filter(slug=candidate).exists(): candidate, n = f"{base}-{n}", n + 1
            self.slug = candidate
        super().save(*args, **kwargs)
    @property
    def prix_actuel(self):
        return self.prix_promotionnel if self.prix_promotionnel is not None else self.prix
    @property
    def stock_total(self): return sum(v.stock for v in self.variantes.filter(active=True))
    def get_absolute_url(self): return reverse("zendo:produit_detail", args=[self.slug])
    def __str__(self): return self.nom

class ImageProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="produits/%Y/%m/")
    texte_alt = models.CharField(max_length=180, blank=True)
    principale = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["ordre", "id"]

class VarianteProduit(TimeStampedModel):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="variantes")
    sku = models.CharField(max_length=70, unique=True)
    taille = models.CharField(max_length=40, blank=True)
    couleur = models.CharField(max_length=60, blank=True)
    modele = models.CharField(max_length=80, blank=True)
    supplement_prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    seuil_alerte = models.PositiveIntegerField(default=5)
    active = models.BooleanField(default=True)
    class Meta: constraints = [models.UniqueConstraint(fields=["produit", "taille", "couleur", "modele"], name="variante_unique")]
    @property
    def prix(self): return self.produit.prix_actuel + self.supplement_prix
    @property
    def stock_faible(self): return self.stock <= self.seuil_alerte
    def __str__(self): return " / ".join(filter(None, [self.produit.nom, self.taille, self.couleur, self.modele]))

class MouvementStock(TimeStampedModel):
    TYPES = [("entree", "Entrée"), ("vente", "Vente"), ("retour", "Retour"), ("ajustement", "Ajustement"), ("perte", "Perte")]
    variante = models.ForeignKey(VarianteProduit, on_delete=models.PROTECT, related_name="mouvements")
    type_mouvement = models.CharField(max_length=20, choices=TYPES)
    quantite = models.IntegerField()
    stock_apres = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    utilisateur = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: ordering = ["-cree_le"]

class Coupon(TimeStampedModel):
    TYPES = [("pourcentage", "Pourcentage"), ("montant", "Montant fixe")]
    code = models.CharField(max_length=30, unique=True)
    type_remise = models.CharField(max_length=20, choices=TYPES)
    valeur = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    minimum_commande = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debut = models.DateTimeField(default=timezone.now)
    fin = models.DateTimeField()
    limite_utilisations = models.PositiveIntegerField(default=0, help_text="0 = illimité")
    utilisations = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    def est_valide(self, sous_total=0):
        now = timezone.now()
        return self.actif and self.debut <= now <= self.fin and sous_total >= self.minimum_commande and (not self.limite_utilisations or self.utilisations < self.limite_utilisations)
    def calculer(self, montant):
        if self.type_remise == "pourcentage": return min(montant, montant * self.valeur / 100)
        return min(montant, self.valeur)
    def __str__(self): return self.code

class Favori(TimeStampedModel):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favoris_zendo")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="dans_favoris")
    class Meta: constraints = [models.UniqueConstraint(fields=["client", "produit"], name="favori_unique")]

class Panier(TimeStampedModel):
    client = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name="panier_zendo")
    session_key = models.CharField(max_length=50, blank=True, db_index=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    actif = models.BooleanField(default=True)
    @property
    def sous_total(self): return sum(i.total for i in self.lignes.select_related("variante__produit"))
    @property
    def remise(self): return self.coupon.calculer(self.sous_total) if self.coupon and self.coupon.est_valide(self.sous_total) else Decimal("0")
    @property
    def total(self): return max(Decimal("0"), self.sous_total - self.remise)

class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name="lignes")
    variante = models.ForeignKey(VarianteProduit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    personnalisation = models.TextField(blank=True)
    fichier_personnalisation = models.FileField(upload_to="personnalisations/", blank=True)
    @property
    def prix_unitaire(self): return self.variante.prix
    @property
    def total(self): return self.prix_unitaire * self.quantite
    class Meta: constraints = [models.UniqueConstraint(fields=["panier", "variante", "personnalisation"], name="ligne_panier_unique")]

class Adresse(TimeStampedModel):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="adresses_zendo")
    nom_complet = models.CharField(max_length=150)
    telephone = models.CharField(max_length=30)
    adresse1 = models.CharField(max_length=180)
    adresse2 = models.CharField(max_length=180, blank=True)
    ville = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True)
    code_postal = models.CharField(max_length=20, blank=True)
    pays = models.CharField(max_length=100)
    principale = models.BooleanField(default=False)
    def __str__(self): return f"{self.nom_complet}, {self.ville}"
class Commande(TimeStampedModel):

    STATUTS = [
        ("brouillon", "Brouillon"),
        ("attente", "En attente"),
        ("confirmee", "Confirmée"),
        ("preparation", "En préparation"),
        ("expediee", "Expédiée"),
        ("livree", "Livrée"),
        ("annulee", "Annulée"),
        ("remboursee", "Remboursée"),
    ]

    numero = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    client = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="commandes_zendo"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default="attente"
    )

    adresse_livraison = models.ForeignKey(
        Adresse,
        on_delete=models.PROTECT,
        related_name="commandes"
    )

    sous_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    remise = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    livraison = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    tps = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    tvq = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    coupon_code = models.CharField(
        max_length=30,
        blank=True
    )

    note_client = models.TextField(
        blank=True
    )

    # ======================================================
    # RELANCE DE PAIEMENT
    # ======================================================

    derniere_relance_paiement = models.DateTimeField(
        null=True,
        blank=True
    )

    nombre_relances_paiement = models.PositiveIntegerField(
        default=0
    )

    def save(self, *args, **kwargs):

        if not self.numero:
            self.numero = (
                f"ZEN-{timezone.now():%Y%m%d}-"
                f"{timezone.now().strftime('%H%M%S%f')[-9:]}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.numero

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    variante = models.ForeignKey(VarianteProduit, null=True, on_delete=models.SET_NULL)
    produit_nom = models.CharField(max_length=180)
    sku = models.CharField(max_length=70)
    details_variante = models.CharField(max_length=200, blank=True)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    personnalisation = models.TextField(blank=True)
    @property
    def total(self): return self.prix_unitaire * self.quantite

class Paiement(TimeStampedModel):
    STATUTS = [("attente", "En attente"), ("autorise", "Autorisé"), ("paye", "Payé"), ("echoue", "Échoué"), ("rembourse", "Remboursé")]
    METHODES = [("stripe", "Carte bancaire"), ("paypal", "PayPal"), ("interac", "Interac"), ("lien", "Lien de paiement"), ("manuel", "Paiement manuel")]
    commande = models.ForeignKey(Commande, on_delete=models.PROTECT, related_name="paiements")
    methode = models.CharField(max_length=20, choices=METHODES)
    statut = models.CharField(max_length=20, choices=STATUTS, default="attente")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    reference_externe = models.CharField(max_length=150, blank=True)
    lien_paiement = models.URLField(blank=True)
    paye_le = models.DateTimeField(null=True, blank=True)

class Facture(TimeStampedModel):
    numero = models.CharField(max_length=30, unique=True, editable=False)
    commande = models.OneToOneField(Commande, on_delete=models.PROTECT, related_name="facture")
    fichier_pdf = models.FileField(upload_to="factures/%Y/%m/", blank=True)
    envoyee = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.numero: self.numero = f"FAC-{timezone.now():%Y%m%d}-{self.commande_id:06d}"
        super().save(*args, **kwargs)
    def __str__(self): return self.numero

class Livraison(TimeStampedModel):
    STATUTS = [("preparation", "Préparation"), ("expediee", "Expédiée"), ("transit", "En transit"), ("livree", "Livrée"), ("retour", "Retournée")]
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name="suivi_livraison")
    transporteur = models.CharField(max_length=100, blank=True)
    numero_suivi = models.CharField(max_length=120, blank=True)
    url_suivi = models.URLField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default="preparation")
    date_expedition = models.DateTimeField(null=True, blank=True)
    livraison_prevue = models.DateField(null=True, blank=True)

class Avis(TimeStampedModel):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="avis")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avis_zendo")
    note = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    titre = models.CharField(max_length=120)
    commentaire = models.TextField()
    approuve = models.BooleanField(default=False)
    class Meta: constraints = [models.UniqueConstraint(fields=["produit", "client"], name="avis_unique")]

class Remboursement(TimeStampedModel):
    STATUTS = [("demande", "Demandé"), ("approuve", "Approuvé"), ("refuse", "Refusé"), ("effectue", "Effectué")]
    paiement = models.ForeignKey(Paiement, on_delete=models.PROTECT, related_name="remboursements")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUTS, default="demande")

class Notification(TimeStampedModel):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_zendo")
    titre = models.CharField(max_length=160)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True)
    lue = models.BooleanField(default=False)

class TicketSupport(TimeStampedModel):
    STATUTS = [("ouvert", "Ouvert"), ("cours", "En cours"), ("ferme", "Fermé")]
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets_zendo")
    sujet = models.CharField(max_length=180)
    message = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUTS, default="ouvert")
    assigne_a = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets_assignes_zendo")

class MessageSupport(TimeStampedModel):
    ticket = models.ForeignKey(TicketSupport, on_delete=models.CASCADE, related_name="messages")
    auteur = models.ForeignKey(User, on_delete=models.PROTECT)
    contenu = models.TextField()

class EvenementCalendrier(TimeStampedModel):
    TYPES = [("tache", "Tâche"), ("rendez_vous", "Rendez-vous"), ("promotion", "Promotion"), ("autre", "Autre")]
    titre = models.CharField(max_length=160)
    type_evenement = models.CharField(max_length=20, choices=TYPES, default="tache")
    debut = models.DateTimeField()
    fin = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    assigne_a = models.ManyToManyField(User, blank=True, related_name="evenements_zendo")
    termine = models.BooleanField(default=False)

class FAQ(TimeStampedModel):
    question = models.CharField(max_length=255)
    reponse = models.TextField()
    ordre = models.PositiveIntegerField(default=0)
    publiee = models.BooleanField(default=True)
    class Meta: ordering = ["ordre", "question"]

def retirer_stock(variante, quantite, reference, utilisateur=None):
    with transaction.atomic():
        verrou = VarianteProduit.objects.select_for_update().get(pk=variante.pk)
        if verrou.stock < quantite: raise ValueError(f"Stock insuffisant pour {verrou}")
        verrou.stock = F("stock") - quantite; verrou.save(update_fields=["stock"]); verrou.refresh_from_db()
        MouvementStock.objects.create(variante=verrou, type_mouvement="vente", quantite=-quantite, stock_apres=verrou.stock, reference=reference, utilisateur=utilisateur)




from django.db import models


class DemandePersonnalisation(models.Model):

    TYPE_CLIENT_CHOICES = [
        ("particulier", "Particulier"),
        ("entreprise", "Entreprise"),
    ]

    STATUT_CHOICES = [
        ("nouvelle", "Nouvelle demande"),
        ("traitement", "En traitement"),
        ("terminee", "Terminée"),
        ("annulee", "Annulée"),
    ]

    type_client = models.CharField(
        max_length=20,
        choices=TYPE_CLIENT_CHOICES,
        default="particulier",
        verbose_name="Type de client",
    )

    nom = models.CharField(
        max_length=150,
        verbose_name="Nom complet",
    )

    nom_entreprise = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nom de l’entreprise",
    )

    telephone = models.CharField(
        max_length=30,
        verbose_name="Numéro de téléphone",
    )

    email = models.EmailField(
        verbose_name="Adresse email",
    )

    code_postal = models.CharField(
        max_length=20,
        verbose_name="Code postal",
    )

    quantite = models.PositiveIntegerField(
        default=1,
        verbose_name="Nombre de pièces",
    )

    couleur = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Couleur souhaitée",
    )

    taille = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Taille(s)",
    )

    description = models.TextField(
        verbose_name="Description de la demande",
    )

    fichier = models.FileField(
        upload_to="personnalisation/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Logo, image ou plan",
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="nouvelle",
    )

    cree_le = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        if self.nom_entreprise:
            return f"{self.nom_entreprise} — {self.nom}"

        return self.nom

    class Meta:
        verbose_name = "Demande de personnalisation"
        verbose_name_plural = "Demandes de personnalisation"
        ordering = ["-cree_le"]