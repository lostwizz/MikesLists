#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
app_pet/views.py
Pet dashboard, GitHub sync, coverage runner, admin action feed.
"""
###############################################################################
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import requests

from .models import DigitalPet

logger = logging.getLogger(__name__)


###############################################################################
# HELPERS
###############################################################################
def get_stage_info(stage):
    """Get evolution stage metadata."""
    stages = {
        'ember':   {'emoji': '🌑', 'next_at': 5,    'prev': None},
        'spark':   {'emoji': '✨', 'next_at': 20,   'prev': 'ember'},
        'flicker': {'emoji': '🔥', 'next_at': 50,   'prev': 'spark'},
        'flame':   {'emoji': '🌟', 'next_at': 100,  'prev': 'flicker'},
        'blaze':   {'emoji': '💫', 'next_at': 200,  'prev': 'flame'},
        'nova':    {'emoji': '⭐', 'next_at': None, 'prev': 'blaze'},
    }
    return stages.get(stage, stages['spark'])


def build_pet_context(pet):
    """Build the full context dict for the pet dashboard."""
    stage_info  = get_stage_info(pet.stage)
    next_at     = stage_info['next_at']

    # Progress towards next evolution (0-100%)
    if next_at:
        progress = min(100, round((pet.total_commits / next_at) * 100))
    else:
        progress = 100   # max stage

    return {
        'pet':          pet,
        'stage_info':   stage_info,
        'progress':     progress,
        'mood_emoji':   pet.mood_emoji,
        'stage_emoji':  pet.stage_emoji,
        'hunger_bar':   pet.hunger_bar,
        'hunger_status': pet.hunger_status,
    }


###############################################################################
# VIEWS
###############################################################################
@login_required
def pet_dashboard(request):
    """Display the pet dashboard."""
    pet, created = DigitalPet.objects.get_or_create(user=request.user)

    if created:
        logger.info(f"New pet created for {request.user.username}")

    # Run daily tick if needed (lazy approach - no cron required)
    from datetime import date
    if pet.updated_at.date() < date.today():
        pet.daily_tick()

    return render(request, 'app_pet/pet_dashboard.html', build_pet_context(pet))


@login_required
def fetch_github_commits(request):
    """Fetch today's commits from GitHub API and feed the pet."""
    username = request.user.profile.github_username
    if not username:
        return JsonResponse({'error': 'No GitHub username set in profile'}, status=400)

    url = f'https://api.github.com/users/{username}/events'
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        return JsonResponse({'error': f'GitHub API unreachable: {e}'}, status=503)

    if response.status_code != 200:
        return JsonResponse({'error': f'GitHub API error: {response.status_code}'}, status=400)

    events = response.json()

    # Count only today's PushEvents
    from datetime import date
    today_str = date.today().isoformat()
    commits_today = sum(
        1 for e in events
        if e.get('type') == 'PushEvent'
        and e.get('created_at', '').startswith(today_str)
    )

    pet = request.user.pet
    pet.feed(commits_today)

    return JsonResponse({
        'commits':      commits_today,
        'stage':        pet.stage,
        'stage_emoji':  pet.stage_emoji,
        'mood':         pet.mood,
        'mood_emoji':   pet.mood_emoji,
        'hunger':       pet.hunger,
        'hunger_bar':   pet.hunger_bar,
        'hunger_status': pet.hunger_status,
        'xp':           pet.xp,
        'total_commits': pet.total_commits,
        'commit_streak': pet.commit_streak,
    })


@login_required
def run_coverage(request):
    """
    Run pytest coverage and update the pet's coverage score.
    POST only - this is a slow operation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    pet = request.user.pet
    project_path = settings.BASE_DIR
    venv_path    = str(settings.BASE_DIR.parent / f'venv-{settings.ENV_NAME}')

    score, output = pet.update_coverage(project_path, venv_path)

    if score is None:
        return JsonResponse({'error': 'Coverage run failed', 'output': output}, status=500)

    return JsonResponse({
        'coverage':     score,
        'xp':           pet.xp,
        'mood':         pet.mood,
        'mood_emoji':   pet.mood_emoji,
        'hunger':       pet.hunger,
        'hunger_bar':   pet.hunger_bar,
    })
