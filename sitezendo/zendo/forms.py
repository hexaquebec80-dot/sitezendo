from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Adresse, Avis, Coupon, EvenementCalendrier, Produit, TicketSupport, VarianteProduit

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
            "nom": forms.TextInput(
                attrs={
                    "placeholder": "Exemple : Ensemble africain premium",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "placeholder": "ensemble-africain-premium",
                }
            ),
            "sku": forms.TextInput(
                attrs={
                    "placeholder": "Exemple : ZEN-001",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Décrivez le produit, sa matière, son style "
                        "et ses caractéristiques..."
                    ),
                }
            ),
            "prix": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "0.00",
                }
            ),
            "prix_promotionnel": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Prix promotionnel facultatif",
                }
            ),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "multiple-select",
                }
            ),
        }
from django import forms
from django.forms import inlineformset_factory

from .models import Produit, ImageProduit, VarianteProduit


class ImageProduitForm(forms.ModelForm):
    class Meta:
        model = ImageProduit
        fields = "__all__"

        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
        }


class VarianteProduitForm(forms.ModelForm):
    class Meta:
        model = VarianteProduit
        fields = "__all__"


ImageProduitFormSet = inlineformset_factory(
    Produit,
    ImageProduit,
    form=ImageProduitForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


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
                }
            ),

            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Votre nom complet",
                }
            ),

            "nom_entreprise": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom de votre entreprise",
                }
            ),

            "telephone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. +1 514 000 0000",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "vous@exemple.com",
                }
            ),

            "code_postal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. G7H 0A1",
                }
            ),

            "quantite": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Nombre de pièces",
                }
            ),

            "couleur": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. Noir, blanc, rouge...",
                }
            ),

            "taille": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. S, M, L, XL...",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": (
                        "Expliquez votre projet : type de tenue, "
                        "emplacement du logo, texte à imprimer, "
                        "couleurs, dimensions, etc."
                    ),
                }
            ),

            "fichier": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": (
                        ".jpg,.jpeg,.png,.webp,.pdf,"
                        ".svg,.ai,.eps"
                    ),
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        type_client = cleaned_data.get(
            "type_client"
        )

        nom_entreprise = cleaned_data.get(
            "nom_entreprise"
        )

        if (
            type_client == "entreprise"
            and not nom_entreprise
        ):

            self.add_error(
                "nom_entreprise",
                "Veuillez indiquer le nom de votre entreprise.",
            )

        return cleaned_data