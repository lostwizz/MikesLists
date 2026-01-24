#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_signals.py
accounts.tests.test_signals
/srv/django/MikesLists_dev/accounts/tests/test_signals.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 00:59:36"
###############################################################################
# /srv/django/venv-dev/bin/python /srv/django/MikesLists_dev/manage.py test app_accounts.tests --settings=MikesLists.settings.dev --noinput -v 3 --debug-mode --traceback --force-color --shuffle
# python manage.py test app_accounts.tests --settings=MikesLists.settings.dev --noinput -v 3 --debug-mode --traceback --force-color --shuffle
# python manage.py test app_accounts.tests --settings=MikesLists.settings.dev
# python manage.py test app_accounts --settings=MikesLists.settings.dev


from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from accounts.models import Profile,   create_user_profile, save_user_profile
#from accounts.signals import create_user_profile, save_user_profile

from django.core import mail

class TestSignals(TestCase):
    def test_create_user_profile(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_save_user_profile(self):
        # user = User.objects.create_user(username='testuser', password='testpassword')
        # profile = Profile.objects.create(user=user)
        # user.save()
        # self.assertEqual(profile.user, user)
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.assertEqual(user.profile.user, user)



    def test_assign_read_only_group(self):
        group = Group.objects.create(name='Read Only')
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.assertIn(group, user.groups.all())


# Your test is asserting behavior that does not exist anywhere in your code.
# There is no signal, no model method, no hook that sends:

#     def test_save_user_profile_email(self):
#         user = User.objects.create_user(username='testuser', password='testpassword')
#         profile = Profile.objects.create(user=user)
#         user.save()
#         self.assertEqual(profile.user, user)
#         self.assertEqual(len(mail.outbox), 1)
#         email = mail.outbox[0]
#         self.assertEqual(email.subject, 'Your MikesLists account has been updated')
#         self.assertEqual(email.to, [user.email])
