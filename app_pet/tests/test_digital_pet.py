#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from django.contrib.auth.models import User
from app_pet.models import DigitalPet

@pytest.mark.django_db
def test_digital_pet_creation():
    """Test that a DigitalPet can be created with default values"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user)
    
    assert pet.name == "CodeBuddy"
    assert pet.stage == "spark"
    assert pet.commits_today == 0
    assert pet.total_commits == 0

@pytest.mark.django_db
def test_evolve_spark_to_flicker():
    """Test evolution from spark to flicker at 5 commits"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='spark', total_commits=5)
    
    pet.evolve()
    
    assert pet.stage == 'flicker'

@pytest.mark.django_db
def test_evolve_flicker_to_flame():
    """Test evolution from flicker to flame at 20 commits"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='flicker', total_commits=20)
    
    pet.evolve()
    
    assert pet.stage == 'flame'

@pytest.mark.django_db
def test_evolve_flame_to_blaze():
    """Test evolution from flame to blaze at 50 commits"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='flame', total_commits=50)
    
    pet.evolve()
    
    assert pet.stage == 'blaze'

@pytest.mark.django_db
def test_evolve_blaze_to_nova():
    """Test evolution from blaze to nova at 100 commits"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='blaze', total_commits=100)
    
    pet.evolve()
    
    assert pet.stage == 'nova'

@pytest.mark.django_db
def test_feed_increments_commits():
    """Test that feeding increments all commit counters"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user)
    
    pet.feed(3)
    
    assert pet.commits_today == 3
    assert pet.commits_this_week == 3
    assert pet.total_commits == 3

@pytest.mark.django_db
def test_feed_triggers_evolution():
    """Test that feeding with enough commits triggers evolution"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='spark', total_commits=3)
    
    pet.feed(2)
    
    assert pet.stage == 'flicker'
    assert pet.total_commits == 5
