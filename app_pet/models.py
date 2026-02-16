# app_pet/models.py
from django.db import models
from django.contrib.auth.models import User

class DigitalPet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pet')
    name = models.CharField(max_length=50, default="CodeBuddy")

    # Evolution stages
    STAGES = [
        ('spark', 'Spark'),
        ('flicker', 'Flicker'),
        ('flame', 'Flame'),
        ('blaze', 'Blaze'),
        ('nova', 'Nova'),
    ]
    stage = models.CharField(max_length=10, choices=STAGES, default='spark')

    # Stats
    commits_today = models.IntegerField(default=0)
    commits_this_week = models.IntegerField(default=0)
    total_commits = models.IntegerField(default=0)

    # Mood/status
    mood = models.CharField(max_length=20, default='happy')
    last_fed = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def evolve(self):
        """Check if pet should evolve based on commits"""
        if self.total_commits >= 100 and self.stage == 'blaze':
            self.stage = 'nova'
        elif self.total_commits >= 50 and self.stage == 'flame':
            self.stage = 'blaze'
        elif self.total_commits >= 20 and self.stage == 'flicker':
            self.stage = 'flame'
        elif self.total_commits >= 5 and self.stage == 'spark':
            self.stage = 'flicker'
        self.save()

    def feed(self, commits):
        """Feed the pet with commits"""
        self.commits_today += commits
        self.commits_this_week += commits
        self.total_commits += commits
        self.evolve()
        self.save()
