#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
#!/usr/bin/env python

import os
import sys


def main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "sitezendo.settings",
    )

    try:
        from django.core.management import (
            execute_from_command_line,
        )
    except ImportError as erreur:
        raise ImportError(
            "Django n’est pas installé. "
            "Exécutez : py -m pip install Django"
        ) from erreur

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()