# app_pet/management/commands/reset_daily_stats.py
from django.core.management.base import BaseCommand
from app_pet.models import DigitalPet

class Command(BaseCommand):
    help = 'Reset daily commit counts'

    def handle(self, *args, **options):
        DigitalPet.objects.all().update(commits_today=0)
        self.stdout.write(self.style.SUCCESS('Daily stats reset'))
