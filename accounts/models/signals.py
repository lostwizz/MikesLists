#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
signals.py
accounts.models.signals
/srv/django/MikesLists_dev/accounts/models/signals.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 23:30:01"
###############################################################################


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .profile import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # This ensures the profile is saved whenever the user is saved
    if hasattr(instance, 'profile'):
        instance.profile.save()
