#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
app_pet/signals.py
Signals to hook pet updates into Django events:
  - user_logged_in  → update login streak + mood
  - admin log_entry → award admin action XP
"""
###############################################################################
import logging
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry

logger = logging.getLogger(__name__)


###############################################################################
# LOGIN STREAK
###############################################################################
@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    """
    Fire on every login.
    Updates login streak, replenishes hunger slightly, updates mood.
    """
    try:
        pet = user.pet
    except Exception:
        return   # pet doesn't exist yet - no problem

    try:
        pet.update_login_streak()
        pet.update_mood()
        pet.save()
        logger.debug(
            f"Pet login tick: {user.username} "
            f"streak={pet.login_streak} "
            f"mood={pet.mood} "
            f"hunger={pet.hunger}"
        )
    except Exception as e:
        logger.error(f"Pet login signal error for {user.username}: {e}")


###############################################################################
# ADMIN ACTION XP
###############################################################################
@receiver(post_save, sender=LogEntry)
def on_admin_action(sender, instance, created, **kwargs):
    """
    Fire whenever a Django admin action is logged (add/change/delete).
    Awards XP to the acting user's pet.
    """
    if not created:
        return   # only award on new log entries

    try:
        pet = instance.user.pet
    except Exception:
        return   # user has no pet

    try:
        points = pet.award_admin_action()
        logger.debug(
            f"Pet admin XP: {instance.user.username} "
            f"+{points}xp action={instance.get_action_flag_display()}"
        )
    except Exception as e:
        logger.error(f"Pet admin signal error for {instance.user.username}: {e}")
