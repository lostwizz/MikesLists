#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, Mock
from app_pet.models import DigitalPet
from app_pet.views import get_stage_info


def test_get_stage_info_spark():
    """Test get_stage_info returns correct data for spark stage"""
    info = get_stage_info('spark')
    assert info['emoji'] == '✨'
    assert info['next_at'] == 5


def test_get_stage_info_nova():
    """Test get_stage_info returns correct data for nova stage"""
    info = get_stage_info('nova')
    assert info['emoji'] == '⭐'
    assert info['next_at'] is None


def test_get_stage_info_invalid_stage():
    """Test get_stage_info returns spark data for invalid stage"""
    info = get_stage_info('invalid_stage')
    assert info['emoji'] == '✨'


@pytest.mark.django_db
def test_pet_dashboard_requires_login(client):
    """Test that pet dashboard requires authentication"""
    url = reverse('pet:dashboard')
    response = client.get(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


@pytest.mark.django_db
def test_pet_dashboard_creates_pet_if_not_exists(client):
    """Test that pet dashboard creates a pet if user doesn't have one"""
    user = User.objects.create_user(username="testuser", password="x")
    client.login(username="testuser", password="x")
    
    assert not DigitalPet.objects.filter(user=user).exists()
    
    url = reverse('pet:dashboard')
    response = client.get(url)
    
    assert response.status_code == 200
    assert DigitalPet.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_pet_dashboard_includes_stage_info(client):
    """Test that pet dashboard includes stage info in context"""
    user = User.objects.create_user(username="testuser", password="x")
    DigitalPet.objects.create(user=user, stage='flame')
    client.login(username="testuser", password="x")
    
    url = reverse('pet:dashboard')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'stage_info' in response.context
    assert response.context['stage_info']['emoji'] == '🌟'


@pytest.mark.django_db
def test_fetch_github_commits_requires_login(client):
    """Test that fetch_github_commits requires authentication"""
    url = reverse('pet:sync_github')
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_fetch_github_commits_no_username_set(client):
    """Test error when user has no GitHub username"""
    user = User.objects.create_user(username="testuser", password="x")
    client.login(username="testuser", password="x")
    
    url = reverse('pet:sync_github')
    response = client.get(url)
    
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data


@pytest.mark.django_db
@patch('app_pet.views.requests.get')
def test_fetch_github_commits_success(mock_get, client):
    """Test successful GitHub API fetch and pet feeding"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, total_commits=0)
    
    user.profile.github_username = "testgithubuser"
    user.profile.save()
    
    client.login(username="testuser", password="x")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {'type': 'PushEvent'},
        {'type': 'PushEvent'},
        {'type': 'IssueEvent'},
    ]
    mock_get.return_value = mock_response
    
    url = reverse('pet:sync_github')
    response = client.get(url)
    
    assert response.status_code == 200
    data = response.json()
    assert data['commits'] == 2
    
    pet.refresh_from_db()
    assert pet.total_commits == 2


@pytest.mark.django_db
@patch('app_pet.views.requests.get')
def test_fetch_github_commits_api_error(mock_get, client):
    """Test handling of GitHub API error"""
    user = User.objects.create_user(username="testuser", password="x")
    DigitalPet.objects.create(user=user)
    
    user.profile.github_username = "testgithubuser"
    user.profile.save()
    
    client.login(username="testuser", password="x")
    
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    url = reverse('pet:sync_github')
    response = client.get(url)
    
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data


def test_pet_dashboard_url_resolves():
    """Test that pet dashboard URL resolves correctly"""
    url = reverse('pet:dashboard')
    assert url == '/pet/'


def test_sync_github_url_resolves():
    """Test that sync GitHub URL resolves correctly"""
    url = reverse('pet:sync_github')
    assert url == '/pet/sync-github/'
