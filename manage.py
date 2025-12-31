#!/usr/bin/env python
import os  # <--- THIS WAS MISSING
import sys

def main():
    """Run administrative tasks."""
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        # Look at the physical path of this file, not the current working directory
        file_path = os.path.abspath(__file__)
        if "MikesLists_live" in file_path:
            os.environ['DJANGO_SETTINGS_MODULE'] = 'MikesLists.settings.live'
        elif "MikesLists_test" in file_path:
            os.environ['DJANGO_SETTINGS_MODULE'] = 'MikesLists.settings.test'
        else:
            os.environ['DJANGO_SETTINGS_MODULE'] = 'MikesLists.settings.dev'

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
