from pathlib import Path

import os

import dj_database_url

from dotenv import load_dotenv


# ============================================================
# CHEMIN PRINCIPAL DU PROJET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# VARIABLES D'ENVIRONNEMENT
# ============================================================

load_dotenv(
    BASE_DIR / ".env"
)


# ============================================================
# SÉCURITÉ
# ============================================================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "zendo-cle-locale-a-remplacer-en-production",
)


DEBUG = os.environ.get(
    "DEBUG",
    "True",
).lower() == "true"

ALLOWED_HOSTS = [
    domaine.strip()
    for domaine in os.environ.get(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost,sitezendo.onrender.com",
    ).split(",")
    if domaine.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origine.strip()
    for origine in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://sitezendo.onrender.com",
    ).split(",")
    if origine.strip()
]



# ============================================================
# URL PUBLIQUE DU SITE
# ============================================================

SITE_URL = os.environ.get(
    "SITE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ============================================================
# CLOUDINARY
# ============================================================

CLOUDINARY_STORAGE = {

    "CLOUD_NAME": os.environ.get(
        "CLOUDINARY_CLOUD_NAME",
        "",
    ),

    "API_KEY": os.environ.get(
        "CLOUDINARY_API_KEY",
        "",
    ),

    "API_SECRET": os.environ.get(
        "CLOUDINARY_API_SECRET",
        "",
    ),

}


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Cloudinary
    "cloudinary_storage",
    "cloudinary",

    # Zendo Afrique
    "zendo.apps.ZendoConfig",

]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise doit être juste après SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.locale.LocaleMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


# ============================================================
# URL PRINCIPALE
# ============================================================

ROOT_URLCONF = "sitezendo.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [

    {

        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth."
                "context_processors.auth",

                "django.contrib.messages."
                "context_processors.messages",

                # Compteur panier Zendo Afrique
                "zendo.context_processors.compteur_panier",

            ],

        },

    },

]


# ============================================================
# WSGI / ASGI
# ============================================================

WSGI_APPLICATION = "sitezendo.wsgi.application"

ASGI_APPLICATION = "sitezendo.asgi.application"


# ============================================================
# BASE DE DONNÉES
# ============================================================

DATABASES = {

    "default": dj_database_url.config(

        # SQLite en local si DATABASE_URL n'existe pas
        default=(
            f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
        ),

        conn_max_age=600,

        ssl_require=not DEBUG,

    )

}


# ============================================================
# VALIDATION DES MOTS DE PASSE
# ============================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },

]


# ============================================================
# LANGUE
# ============================================================

LANGUAGE_CODE = "fr-ca"


# ============================================================
# FUSEAU HORAIRE
# ============================================================

TIME_ZONE = "America/Toronto"

USE_I18N = True

USE_TZ = True


# ============================================================
# FICHIERS STATIQUES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []


# ============================================================
# STOCKAGE
# ============================================================

STORAGES = {

    # ========================================================
    # MÉDIAS
    # Images produits, logos clients, images uploadées,
    # fichiers de personnalisation, etc.
    # ========================================================

    "default": {

        "BACKEND": (
            "cloudinary_storage.storage."
            "MediaCloudinaryStorage"
        ),

    },


    # ========================================================
    # FICHIERS STATIQUES
    # CSS / JS / images du design
    # ========================================================

    "staticfiles": {

        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),

    },

}


# ============================================================
# FICHIERS MÉDIAS
# ============================================================

# Les médias sont maintenant stockés sur Cloudinary.

MEDIA_URL = "/media/"

# MEDIA_ROOT n'est plus nécessaire avec Cloudinary.


# ============================================================
# AUTHENTIFICATION
# ============================================================

LOGIN_URL = "zendo:connexion"

LOGIN_REDIRECT_URL = "zendo:accueil"

LOGOUT_REDIRECT_URL = "zendo:accueil"


# ============================================================
# COURRIEL — GMAIL SMTP
# ============================================================

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)


EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
    "smtp.gmail.com",
)


EMAIL_PORT = int(
    os.environ.get(
        "EMAIL_PORT",
        "587",
    )
)


EMAIL_USE_TLS = (
    os.environ.get(
        "EMAIL_USE_TLS",
        "True",
    ).lower()
    == "true"
)


EMAIL_USE_SSL = False


EMAIL_HOST_USER = os.environ.get(
    "ZENDO_EMAIL",
    "",
)


EMAIL_HOST_PASSWORD = os.environ.get(
    "ZENDO_EMAIL_PASSWORD",
    "",
)


DEFAULT_FROM_EMAIL = (
    f"Zendo Afrique <{EMAIL_HOST_USER}>"
)


SERVER_EMAIL = DEFAULT_FROM_EMAIL


EMAIL_TIMEOUT = 20


# ============================================================
# EMAIL DESTINATAIRE ZENDO
# ============================================================

ZENDO_CONTACT_EMAIL = os.environ.get(
    "ZENDO_CONTACT_EMAIL",
    "zendoafrique@gmail.com",
)


# ============================================================
# STRIPE
# ============================================================

STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY",
    "",
)


STRIPE_WEBHOOK_SECRET = os.environ.get(
    "STRIPE_WEBHOOK_SECRET",
    "",
)


STRIPE_PUBLIC_KEY = os.environ.get(
    "STRIPE_PUBLIC_KEY",
    "",
)


# ============================================================
# OPENAI / IA
# ============================================================

OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "",
)


OPENAI_MODEL = os.environ.get(
    "OPENAI_MODEL",
    "gpt-5.6",
)


# ============================================================
# SÉCURITÉ RENDER / HTTPS
# ============================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG


X_FRAME_OPTIONS = "DENY"

SECURE_CONTENT_TYPE_NOSNIFF = True


# ============================================================
# PARAMÈTRES HTTPS PRODUCTION
# ============================================================

if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_SAMESITE = "Lax"

    CSRF_COOKIE_SAMESITE = "Lax"

    SECURE_HSTS_SECONDS = int(
        os.environ.get(
            "SECURE_HSTS_SECONDS",
            "0",
        )
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = False

    SECURE_HSTS_PRELOAD = False


# ============================================================
# CONFIGURATION DJANGO
# ============================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)