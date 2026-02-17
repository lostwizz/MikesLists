#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
app_pet/models.py
DigitalPet model with mood, hunger, XP, streaks and de-evolution.
"""
###############################################################################
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
import subprocess
import os


class DigitalPet(models.Model):

    #############################################
    # CHOICES
    #############################################
    STAGES = [
        ('ember',   'Ember'),     # de-evolved state (below spark)
        ('spark',   'Spark'),
        ('flicker', 'Flicker'),
        ('flame',   'Flame'),
        ('blaze',   'Blaze'),
        ('nova',    'Nova'),      # max stage
    ]

    MOODS = [
        ('happy',    'Happy'),
        ('content',  'Content'),
        ('tired',    'Tired'),
        ('sad',      'Sad'),
        ('starving', 'Starving'),
    ]

    STAGE_ORDER = ['ember', 'spark', 'flicker', 'flame', 'blaze', 'nova']

    EVOLUTION_THRESHOLDS = {
        'ember':   5,    # ember  → spark   at  5 total commits
        'spark':   20,   # spark  → flicker at 20 total commits
        'flicker': 50,   # flicker→ flame   at 50 total commits
        'flame':   100,  # flame  → blaze   at 100 total commits
        'blaze':   200,  # blaze  → nova    at 200 total commits
    }

    HUNGER_DRAIN_RATES = {
        'happy':    5,    # loses 5 hunger/day when happy
        'content':  8,
        'tired':    10,
        'sad':      12,
        'starving': 15,   # drains faster when starving
    }

    XP_REWARDS = {
        'commit':           10,
        'login_streak_day':  5,
        'admin_action':      3,
        'coverage_80':      20,
        'coverage_95':      50,
        'streak_7_day':    100,   # bonus for 7-day commit streak
        'streak_30_day':   500,   # bonus for 30-day commit streak
    }

    #############################################
    # CORE FIELDS
    #############################################
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pet')
    name            = models.CharField(max_length=50, default='CodeBuddy')
    stage           = models.CharField(max_length=20, choices=STAGES, default='spark')

    #############################################
    # COMMIT TRACKING
    #############################################
    commits_today       = models.IntegerField(default=0)
    commits_this_week   = models.IntegerField(default=0)
    total_commits       = models.IntegerField(default=0)
    last_commit_date    = models.DateField(null=True, blank=True)
    commit_streak       = models.IntegerField(default=0)   # consecutive days with commits

    #############################################
    # MOOD & HUNGER
    #############################################
    mood            = models.CharField(max_length=20, choices=MOODS, default='happy')
    hunger          = models.IntegerField(default=100)     # 0=starving, 100=full

    #############################################
    # XP & PROGRESSION
    #############################################
    xp              = models.IntegerField(default=0)
    coverage_score  = models.FloatField(default=0.0)       # last known test coverage %

    #############################################
    # LOGIN STREAK
    #############################################
    login_streak        = models.IntegerField(default=0)
    last_login_date     = models.DateField(null=True, blank=True)

    #############################################
    # TIMESTAMPS
    #############################################
    last_fed        = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Digital Pet'

    def __str__(self):
        return f"{self.name} ({self.stage}) - {self.user.username}"

    #############################################
    # MOOD CALCULATION
    #############################################
    def calculate_mood(self):
        """Determine mood based on hunger level and days since last commit."""
        today = date.today()
        days_without_commit = 0

        if self.last_commit_date:
            days_without_commit = (today - self.last_commit_date).days
        else:
            days_without_commit = 999   # never committed

        # Hunger takes priority if critically low
        if self.hunger <= 0:
            return 'starving'
        elif self.hunger <= 20:
            return 'sad'
        elif days_without_commit == 0:
            return 'happy'        # committed today
        elif days_without_commit == 1:
            return 'content'      # committed yesterday
        elif days_without_commit <= 3:
            return 'tired'        # few days without commit
        elif days_without_commit <= 7:
            return 'sad'          # a week without commit
        else:
            return 'starving'     # over a week - critical

    def update_mood(self):
        """Recalculate and save mood."""
        self.mood = self.calculate_mood()

    #############################################
    # HUNGER SYSTEM
    #############################################
    def drain_hunger(self, days=1):
        """Drain hunger based on mood and days elapsed."""
        drain = self.HUNGER_DRAIN_RATES.get(self.mood, 10) * days
        self.hunger = max(0, self.hunger - drain)

    def replenish_hunger(self, amount=30):
        """Increase hunger (feeding the pet)."""
        self.hunger = min(100, self.hunger + amount)

    #############################################
    # XP SYSTEM
    #############################################
    def award_xp(self, reason, amount=None):
        """Award XP for a given reason."""
        points = amount or self.XP_REWARDS.get(reason, 0)
        self.xp += points
        return points

    #############################################
    # COMMIT STREAK
    #############################################
    def update_commit_streak(self):
        """Update commit streak based on last_commit_date."""
        today = date.today()

        if self.last_commit_date is None:
            self.commit_streak = 1
        else:
            delta = (today - self.last_commit_date).days
            if delta == 0:
                pass           # already updated today
            elif delta == 1:
                self.commit_streak += 1    # consecutive day!
            else:
                self.commit_streak = 1     # streak broken

        # Award streak bonuses
        if self.commit_streak == 7:
            self.award_xp('streak_7_day')
        elif self.commit_streak == 30:
            self.award_xp('streak_30_day')

        self.last_commit_date = today

    #############################################
    # LOGIN STREAK
    #############################################
    def update_login_streak(self):
        """Update login streak - call on each login."""
        today = date.today()

        if self.last_login_date is None:
            self.login_streak = 1
        else:
            delta = (today - self.last_login_date).days
            if delta == 0:
                return           # already logged in today, no change
            elif delta == 1:
                self.login_streak += 1    # consecutive day!
            else:
                self.login_streak = 1     # streak broken

        self.last_login_date = today
        self.award_xp('login_streak_day')
        self.replenish_hunger(5)    # login gives a small hunger boost

    #############################################
    # EVOLUTION
    #############################################
    def evolve(self):
        """Check and apply forward evolution."""
        threshold = self.EVOLUTION_THRESHOLDS.get(self.stage)
        if threshold is None:
            return False     # already at max (nova)

        if self.total_commits >= threshold:
            idx = self.STAGE_ORDER.index(self.stage)
            if idx < len(self.STAGE_ORDER) - 1:
                self.stage = self.STAGE_ORDER[idx + 1]
                self.replenish_hunger(20)   # evolution gives a hunger boost
                return True
        return False

    def de_evolve(self):
        """Drop one stage when starving too long."""
        idx = self.STAGE_ORDER.index(self.stage)
        if idx > 0:
            self.stage = self.STAGE_ORDER[idx - 1]
            return True
        return False

    def check_de_evolution(self):
        """De-evolve if hunger is 0 and mood is starving."""
        if self.hunger <= 0 and self.mood == 'starving':
            return self.de_evolve()
        return False

    #############################################
    # FEED (COMMITS)
    #############################################
    def feed(self, commit_count):
        """Feed the pet with commits from GitHub."""
        if commit_count <= 0:
            return

        self.commits_today      += commit_count
        self.commits_this_week  += commit_count
        self.total_commits      += commit_count

        # Award XP per commit
        self.award_xp('commit', commit_count * self.XP_REWARDS['commit'])

        # Replenish hunger based on commits (capped per feeding)
        hunger_gain = min(commit_count * 5, 40)
        self.replenish_hunger(hunger_gain)

        # Update streak
        self.update_commit_streak()

        # Recalculate mood
        self.update_mood()

        # Try to evolve
        self.evolve()

        self.last_fed = timezone.now()
        self.save()

    #############################################
    # ADMIN ACTION XP
    #############################################
    def award_admin_action(self):
        """Award XP for performing a Django admin action."""
        points = self.award_xp('admin_action')
        self.replenish_hunger(2)
        self.update_mood()
        self.save()
        return points

    #############################################
    # COVERAGE SCORE
    #############################################
    def update_coverage(self, project_path, venv_path):
        """
        Run pytest with coverage and update coverage_score.
        Returns (score, output) tuple.
        """
        try:
            result = subprocess.run(
                [
                    f'{venv_path}/bin/pytest',
                    '--cov=.',
                    '--cov-report=term-missing',
                    '-q',
                    '--no-header',
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            output = result.stdout + result.stderr

            # Parse coverage percentage from output
            # looks for "TOTAL   xxx   xx   XX%"
            for line in output.split('\n'):
                if line.startswith('TOTAL'):
                    parts = line.split()
                    pct_str = parts[-1].replace('%', '')
                    score = float(pct_str)
                    self.coverage_score = score

                    # Award XP based on coverage level
                    if score >= 95:
                        self.award_xp('coverage_95')
                        self.replenish_hunger(15)
                    elif score >= 80:
                        self.award_xp('coverage_80')
                        self.replenish_hunger(8)

                    self.update_mood()
                    self.save()
                    return score, output

        except (subprocess.TimeoutExpired, Exception) as e:
            return None, str(e)

        return None, output

    #############################################
    # DAILY TICK (call via cron or management command)
    #############################################
    def daily_tick(self):
        """
        Called once per day to update hunger, mood, check de-evolution.
        Wire this to a cron job or Django management command.
        """
        self.update_mood()
        self.drain_hunger(days=1)
        self.update_mood()          # recalculate after drain
        self.check_de_evolution()
        self.save()

    #############################################
    # DISPLAY HELPERS
    #############################################
    @property
    def mood_emoji(self):
        return {
            'happy':    '😊',
            'content':  '😐',
            'tired':    '😴',
            'sad':      '😢',
            'starving': '😵',
        }.get(self.mood, '😐')

    @property
    def stage_emoji(self):
        return {
            'ember':   '🌑',
            'spark':   '✨',
            'flicker': '🔥',
            'flame':   '🌟',
            'blaze':   '💫',
            'nova':    '⭐',
        }.get(self.stage, '✨')

    @property
    def hunger_bar(self):
        """Return hunger as filled/empty blocks for display."""
        filled = round(self.hunger / 10)
        empty  = 10 - filled
        return '█' * filled + '░' * empty

    @property
    def hunger_status(self):
        if self.hunger >= 80:   return 'Full'
        if self.hunger >= 60:   return 'Satisfied'
        if self.hunger >= 40:   return 'Hungry'
        if self.hunger >= 20:   return 'Very Hungry'
        if self.hunger > 0:     return 'Starving!'
        return 'Empty - De-evolving!'
