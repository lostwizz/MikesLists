#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
from .models import DigitalPet

@login_required
def pet_dashboard(request):
    """Display the pet dashboard"""
    pet, created = DigitalPet.objects.get_or_create(user=request.user)

    context = {
        'pet': pet,
        'stage_info': get_stage_info(pet.stage),
    }
    return render(request, 'app_pet/dashboard.html', context)

@login_required
def fetch_github_commits(request):
    """Fetch commits from GitHub API"""
    username = request.user.profile.github_username
    if not username:
        return JsonResponse({'error': 'No GitHub username set'}, status=400)

    url = f'https://api.github.com/users/{username}/events'
    response = requests.get(url)

    if response.status_code == 200:
        events = response.json()
        commits_today = sum(1 for e in events if e['type'] == 'PushEvent')

        pet = request.user.pet
        pet.feed(commits_today)

        return JsonResponse({
            'commits': commits_today,
            'stage': pet.stage,
            'total': pet.total_commits,
        })

    return JsonResponse({'error': 'GitHub API error'}, status=400)

def get_stage_info(stage):
    """Get evolution stage metadata"""
    stages = {
        'spark': {'emoji': '✨', 'next_at': 5},
        'flicker': {'emoji': '🔥', 'next_at': 20},
        'flame': {'emoji': '🌟', 'next_at': 50},
        'blaze': {'emoji': '💫', 'next_at': 100},
        'nova': {'emoji': '⭐', 'next_at': None},
    }
    return stages.get(stage, stages['spark'])
