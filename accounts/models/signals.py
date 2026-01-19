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
__updated__ = "2026-01-19 17:06:17"
###############################################################################


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .profile import Profile
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # 1. Create the profile
        Profile.objects.create(user=instance)

        # 2. Assign the 'Read Only' group

        try:
            group = Group.objects.get(name="Read Only")
            instance.groups.add(group)
        except Group.DoesNotExist:
            # This prevents the app from crashing if you haven't
            # created the group in the Admin panel yet
            admin_emails = User.objects.filter(is_superuser=True).values_list(
                "email", flat=True
            )
            if admin_emails:
                send_mail(
                    "Missing Database Group Notification",
                    f"User '{instance.username}' was created, but the 'Read Only' group does not exist.",
                    "noreply@mikeslists.local",
                    list(admin_emails),
                    fail_silently=True,
                )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # This ensures the profile is saved whenever the user is saved
    if hasattr(instance, "profile"):
        instance.profile.save()
