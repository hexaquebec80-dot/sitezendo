from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Adresse, Avis, Coupon, EvenementCalendrier, Produit, TicketSupport, VarianteProduit
import os

from django import forms
from PIL import Image, UnidentifiedImageError



class InscriptionForm(UserCreationForm):
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    email = forms.EmailField()
    class Meta: model = User; fields = ("first_name", "last_name", "username", "email", "password1", "password2")
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists(): raise forms.ValidationError("Cette adresse est déjà utilisée.")
        return email

class ConnexionForm(AuthenticationForm): pass
class AdresseForm(forms.ModelForm):
    class Meta: model = Adresse; exclude = ("client",); widgets = {"adresse1": forms.TextInput(), "adresse2": forms.TextInput()}
class AjouterPanierForm(forms.Form):
    variante = forms.ModelChoiceField(queryset=VarianteProduit.objects.none())
    quantite = forms.IntegerField(min_value=1, initial=1)
    personnalisation = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    fichier_personnalisation = forms.FileField(required=False)
    def __init__(self, *args, produit=None, **kwargs):
        super().__init__(*args, **kwargs)
        if produit: self.fields["variante"].queryset = produit.variantes.filter(active=True, stock__gt=0)
class CouponForm(forms.Form): code = forms.CharField(max_length=30)
class AvisForm(forms.ModelForm):
    class Meta: model = Avis; fields = ("note", "titre", "commentaire")
class TicketSupportForm(forms.ModelForm):
    class Meta: model = TicketSupport; fields = ("sujet", "message")

    
class EvenementForm(forms.ModelForm):
    class Meta:
        model = EvenementCalendrier; exclude = ("cree_le", "modifie_le")
        widgets = {"debut": forms.DateTimeInput(attrs={"type": "datetime-local"}), "fin": forms.DateTimeInput(attrs={"type": "datetime-local"})}




from django import forms

from .models import Livraison


class LivraisonForm(forms.ModelForm):

    class Meta:
        model = Livraison

        fields = [
            "commande",
            "transporteur",
            "numero_suivi",
            "statut",
            "livraison_prevue",
        ]

        widgets = {
            "commande": forms.Select(
                attrs={
                    "class": "delivery-input",
                }
            ),

            "transporteur": forms.TextInput(
                attrs={
                    "class": "delivery-input",
                    "placeholder": "Exemple : Postes Canada",
                }
            ),

            "numero_suivi": forms.TextInput(
                attrs={
                    "class": "delivery-input",
                    "placeholder": "Exemple : CA123456789",
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "delivery-input",
                }
            ),

            "livraison_prevue": forms.DateInput(
                attrs={
                    "class": "delivery-input",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
        }

        labels = {
            "commande": "Commande associée",
            "transporteur": "Transporteur",
            "numero_suivi": "Numéro de suivi",
            "statut": "Statut de la livraison",
            "livraison_prevue": "Date de livraison prévue",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["livraison_prevue"].input_formats = [
            "%Y-%m-%d",
        ]

        for field in self.fields.values():
            field.required = False

        self.fields["commande"].required = True
        self.fields["statut"].required = True




from django import forms
from django.forms import inlineformset_factory

from .models import Produit, ImageProduit, VarianteProduit

from django import forms
from django.utils.text import slugify

from .models import Produit, Categorie


class ProduitForm(forms.ModelForm):

    class Meta:
        model = Produit

        fields = [
            "nom",
            "slug",
            "sku",
            "categorie",
            "description",
            "prix",
            "prix_promotionnel",
            "actif",
            "vedette",
            "personnalisable",
            "tags",
        ]

        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Exemple : Ensemble africain premium",
            }),

            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Généré automatiquement si vide",
            }),

            "sku": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Exemple : ZEN-001",
            }),

            "categorie": forms.Select(attrs={
                "class": "form-select",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": (
                    "Décrivez le produit, sa matière, "
                    "son style et ses caractéristiques..."
                ),
            }),

            "prix": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "0.00",
            }),

            "prix_promotionnel": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "Prix promotionnel facultatif",
            }),

            "tags": forms.SelectMultiple(attrs={
                "class": "form-select multiple-select",
            }),

            "actif": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "vedette": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "personnalisable": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "nom": "Nom du produit",
            "slug": "Lien du produit (facultatif)",
            "sku": "Référence SKU",
            "categorie": "Catégorie du produit",
            "description": "Description du produit",
            "prix": "Prix normal ($ CAD)",
            "prix_promotionnel": "Prix promotionnel ($ CAD)",
            "actif": "Produit actif",
            "vedette": "Mettre en vedette",
            "personnalisable": "Produit personnalisable",
            "tags": "Étiquettes du produit",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Catégorie obligatoire
        self.fields["categorie"].required = True

        # Catégories actives uniquement
        self.fields["categorie"].queryset = (
            Categorie.objects.filter(active=True)
            .select_related("parent")
            .order_by("ordre", "nom")
        )

        self.fields["categorie"].empty_label = (
            "Sélectionnez une catégorie"
        )

        # Slug facultatif
        self.fields["slug"].required = False

        # Prix promotionnel facultatif
        self.fields["prix_promotionnel"].required = False

        # Tags facultatifs
        self.fields["tags"].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")

        if slug:
            return slugify(slug)

        return ""

    def clean(self):
        cleaned_data = super().clean()

        prix = cleaned_data.get("prix")
        prix_promotionnel = cleaned_data.get(
            "prix_promotionnel"
        )

        if (
            prix is not None
            and prix_promotionnel is not None
            and prix_promotionnel >= prix
        ):
            self.add_error(
                "prix_promotionnel",
                "Le prix promotionnel doit être inférieur au prix normal."
            )

        return cleaned_data

from django import forms
from django.forms import (
    BaseInlineFormSet,
    inlineformset_factory,
)

from .models import (
    Produit,
    ImageProduit,
    VarianteProduit,
)


# =====================================================
# FORMULAIRE IMAGE PRODUIT
# =====================================================

class ImageProduitForm(forms.ModelForm):

    class Meta:
        model = ImageProduit

        fields = [
            "image",
            "texte_alt",
            "principale",
            "ordre",
        ]

        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/jpeg,image/png,image/webp",
                    "class": "form-control",
                }
            ),

            "texte_alt": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description facultative",
                }
            ),

            "principale": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "ordre": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


# =====================================================
# VALIDATION DES IMAGES
# =====================================================

class BaseImageProduitFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        images_valides = []
        principales = []

        for form in self.forms:

            if not form.cleaned_data:
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            image = form.cleaned_data.get("image")

            # Image déjà enregistrée
            if not image and form.instance.pk:
                image = form.instance.image

            if image:
                images_valides.append(form)

                if form.cleaned_data.get("principale"):
                    principales.append(form)

        if len(images_valides) < 1:
            raise forms.ValidationError(
                "Vous devez ajouter au moins une image principale."
            )

        if len(images_valides) > 4:
            raise forms.ValidationError(
                "Un produit ne peut pas contenir plus de 4 images."
            )

        if len(principales) > 1:
            raise forms.ValidationError(
                "Une seule image peut être définie comme principale."
            )

        # Si aucune image principale n'est sélectionnée,
        # la première image sera automatiquement principale.
        if not principales:
            images_valides[0].cleaned_data["principale"] = True


# =====================================================
# FORMULAIRE VARIANTE PRODUIT
# =====================================================

class VarianteProduitForm(forms.ModelForm):

    class Meta:
        model = VarianteProduit
        exclude = ["produit"]


# =====================================================
# FORMSET IMAGES
# =====================================================

ImageProduitFormSet = inlineformset_factory(
    Produit,
    ImageProduit,
    form=ImageProduitForm,
    formset=BaseImageProduitFormSet,
    extra=4,
    can_delete=True,
    min_num=1,
    max_num=4,
    validate_min=True,
    validate_max=True,
)


# =====================================================
# FORMSET VARIANTES
# =====================================================

VarianteProduitFormSet = inlineformset_factory(
    Produit,
    VarianteProduit,
    form=VarianteProduitForm,
    extra=3,
    can_delete=True,
)

from django import forms

from .models import DemandePersonnalisation


class DemandePersonnalisationForm(forms.ModelForm):

    class Meta:

        model = DemandePersonnalisation

        fields = [
            "type_client",
            "nom",
            "nom_entreprise",
            "telephone",
            "email",
            "code_postal",
            "quantite",
            "couleur",
            "taille",
            "description",
            "fichier",
        ]

        widgets = {

            "type_client": forms.Select(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),

            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Votre nom complet",
                    "required": True,
                }
            ),

            "nom_entreprise": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom de votre entreprise",
                    "required": True,
                }
            ),

            "telephone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. +1 418 000 0000",
                    "required": True,
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "exemple@email.com",
                    "required": True,
                }
            ),

            "code_postal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Votre code postal",
                    "required": True,
                }
            ),

            "quantite": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "required": True,
                }
            ),

            "couleur": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. Noir, blanc, vert...",
                    "required": True,
                }
            ),

            "taille": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. 10 × M, 10 × L, 5 × XL",
                    "required": True,
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Décrivez votre projet de personnalisation...",
                    "required": True,
                }
            ),

            "fichier": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "accept": "image/*,.pdf",
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ==============================================
        # TOUS LES CHAMPS SONT OBLIGATOIRES
        # ==============================================

        for field_name, field in self.fields.items():

            field.required = True

            field.widget.attrs["required"] = True


    def clean_nom(self):

        value = self.cleaned_data.get("nom", "").strip()

        if not value:
            raise forms.ValidationError(
                "Veuillez renseigner votre nom complet."
            )

        return value


    def clean_nom_entreprise(self):

        value = self.cleaned_data.get(
            "nom_entreprise",
            ""
        ).strip()

        if not value:
            raise forms.ValidationError(
                "Veuillez renseigner le nom de l’entreprise."
            )

        return value


    def clean_telephone(self):

        value = self.cleaned_data.get(
            "telephone",
            ""
        ).strip()

        if not value:
            raise forms.ValidationError(
                "Veuillez renseigner votre numéro de téléphone."
            )

        return value


    def clean_code_postal(self):

        value = self.cleaned_data.get(
            "code_postal",
            ""
        ).strip()

        if not value:
            raise forms.ValidationError(
                "Veuillez renseigner votre code postal."
            )

        return value


    def clean_couleur(self):

        value = self.cleaned_data.get(
            "couleur",
            ""
        ).strip()

        if not value:
            raise forms.ValidationError(
                "Veuillez préciser la couleur souhaitée."
            )

        return value


    def clean_taille(self):

        value = self.cleaned_data.get(
            "taille",
            ""
        ).strip()

        if not value:
            raise forms.ValidationError(
                "Veuillez préciser la ou les tailles souhaitées."
            )

        return value


    def clean_description(self):

        value = self.cleaned_data.get(
            "description",
            ""
        ).strip()

        if not value:
            raise forms.ValidationError(
                "Veuillez décrire votre demande."
            )

        return value

def clean_fichier(self):

    fichier = self.cleaned_data.get("fichier")

    if not fichier:
        raise forms.ValidationError(
            "Vous devez joindre un fichier original."
        )

    # ==================================================
    # EXTENSIONS AUTORISÉES
    # ==================================================

    extensions_autorisees = [
        ".png",
        ".jpg",
        ".jpeg",
        ".pdf",
        ".svg",
        ".ai",
        ".eps",
    ]

    nom_fichier = fichier.name.lower()

    extension = os.path.splitext(
        nom_fichier
    )[1]

    if extension not in extensions_autorisees:
        raise forms.ValidationError(
            "Format non autorisé. "
            "Formats acceptés : PNG, JPG/JPEG, PDF, SVG, AI et EPS."
        )

    # ==================================================
    # FICHIER VIDE
    # ==================================================

    if fichier.size == 0:
        raise forms.ValidationError(
            "Le fichier envoyé est vide."
        )

    # ==================================================
    # TAILLE MAXIMALE : 20 Mo
    # ==================================================

    taille_max = 20 * 1024 * 1024

    if fichier.size > taille_max:
        raise forms.ValidationError(
            "Le fichier est trop volumineux. "
            "La taille maximale autorisée est de 20 Mo."
        )

    # ==================================================
    # VÉRIFICATION DU TYPE MIME
    # ==================================================

    types_mime_autorises = [
        "image/png",
        "image/jpeg",
        "application/pdf",
        "image/svg+xml",
        "application/postscript",
        "application/illustrator",
        "application/vnd.adobe.illustrator",
        "application/octet-stream",
    ]

    content_type = getattr(
        fichier,
        "content_type",
        ""
    )

    if (
        content_type
        and content_type not in types_mime_autorises
    ):
        raise forms.ValidationError(
            "Le type de fichier envoyé n'est pas autorisé."
        )

    # ==================================================
    # VÉRIFICATION RÉELLE PNG / JPG / JPEG
    # ==================================================

    if extension in [
        ".png",
        ".jpg",
        ".jpeg",
    ]:

        try:

            image = Image.open(fichier)

            image.verify()

            if image.format not in [
                "PNG",
                "JPEG",
            ]:
                raise forms.ValidationError(
                    "Le fichier n'est pas réellement "
                    "une image PNG ou JPEG valide."
                )

            fichier.seek(0)

        except UnidentifiedImageError:

            raise forms.ValidationError(
                "Le fichier image est invalide ou corrompu."
            )

        except forms.ValidationError:
            raise

        except Exception:

            raise forms.ValidationError(
                "Impossible de vérifier cette image."
            )

    # ==================================================
    # VÉRIFICATION SIGNATURE PDF
    # ==================================================

    if extension == ".pdf":

        debut = fichier.read(5)

        fichier.seek(0)

        if debut != b"%PDF-":
            raise forms.ValidationError(
                "Le fichier sélectionné n'est pas "
                "un véritable fichier PDF."
            )

    # ==================================================
    # VÉRIFICATION SVG
    # ==================================================

    if extension == ".svg":

        try:

            contenu = fichier.read(4096).decode(
                "utf-8",
                errors="ignore"
            ).lower()

            fichier.seek(0)

            if "<svg" not in contenu:
                raise forms.ValidationError(
                    "Le fichier sélectionné n'est pas "
                    "un véritable fichier SVG."
                )

        except forms.ValidationError:
            raise

        except Exception:

            raise forms.ValidationError(
                "Impossible de vérifier le fichier SVG."
            )

    return fichier

    def clean_quantite(self):

        quantite = self.cleaned_data.get(
            "quantite"
        )

        if not quantite:
            raise forms.ValidationError(
                "Veuillez préciser le nombre de pièces."
            )

        if quantite < 1:
            raise forms.ValidationError(
                "La quantité doit être supérieure à 0."
            )

        return quantite