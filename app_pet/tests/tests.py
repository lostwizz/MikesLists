#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_digital_pet.py

Comprehensive tests for DigitalPet model to achieve 100% coverage.
"""
###############################################################################

import pytest
from django.contrib.auth.models import User
from app_pet.models import DigitalPet


###############################################################################
# Model Creation Tests
###############################################################################

@pytest.mark.django_db
def test_digital_pet_creation():
    """Test that a DigitalPet can be created with default values"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user)

    assert pet.name == "CodeBuddy"
    assert pet.stage == "spark"
    assert pet.commits_today == 0
    assert pet.commits_this_week == 0
    assert pet.total_commits == 0
    assert pet.mood == "happy"


@pytest.mark.django_db
def test_digital_pet_custom_name():
    """Test creating a pet with a custom name"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, name="Sparky")

    assert pet.name == "Sparky"


###############################################################################
# Evolution Tests - Covers lines 33-41
###############################################################################

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
def test_evolve_no_change_insufficient_commits():
    """Test that pet doesn't evolve without enough commits"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='spark', total_commits=3)

    pet.evolve()

    # Should still be spark (needs 5 commits)
    assert pet.stage == 'spark'


@pytest.mark.django_db
def test_evolve_no_change_at_max_level():
    """Test that nova stage pet doesn't evolve further"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='nova', total_commits=200)

    pet.evolve()

    # Should stay at nova
    assert pet.stage == 'nova'


@pytest.mark.django_db
def test_evolve_wrong_stage_for_threshold():
    """Test that pet doesn't evolve if stage doesn't match threshold"""
    user = User.objects.create_user(username="testuser", password="x")
    # Pet is at 'flame' but has commits for 'nova'
    pet = DigitalPet.objects.create(user=user, stage='flame', total_commits=100)

    pet.evolve()

    # Should only evolve one stage at a time (flame -> blaze, not flame -> nova)
    assert pet.stage == 'blaze'


###############################################################################
# Feed Method Tests - Covers lines 45-49
###############################################################################

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
def test_feed_multiple_times():
    """Test that multiple feedings accumulate"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user)

    pet.feed(2)
    pet.feed(3)

    assert pet.commits_today == 5
    assert pet.commits_this_week == 5
    assert pet.total_commits == 5


@pytest.mark.django_db
def test_feed_triggers_evolution():
    """Test that feeding with enough commits triggers evolution"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user, stage='spark', total_commits=3)

    # Feed 2 more commits to reach 5 total (evolution threshold)
    pet.feed(2)

    # Should have evolved to flicker
    assert pet.stage == 'flicker'
    assert pet.total_commits == 5


@pytest.mark.django_db
def test_feed_saves_to_database():
    """Test that feed method persists changes to database"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user)
    pet_id = pet.id

    pet.feed(5)

    # Retrieve from database to verify persistence
    pet_from_db = DigitalPet.objects.get(id=pet_id)
    assert pet_from_db.total_commits == 5
    assert pet_from_db.stage == 'flicker'


###############################################################################
# Integration Tests
###############################################################################

@pytest.mark.django_db
def test_complete_evolution_journey():
    """Test pet evolving through all stages"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user)

    # Start at spark
    assert pet.stage == 'spark'

    # Feed to flicker (5 commits)
    pet.feed(5)
    assert pet.stage == 'flicker'

    # Feed to flame (20 total commits)
    pet.feed(15)
    assert pet.stage == 'flame'

    # Feed to blaze (50 total commits)
    pet.feed(30)
    assert pet.stage == 'blaze'

    # Feed to nova (100 total commits)
    pet.feed(50)
    assert pet.stage == 'nova'
    assert pet.total_commits == 100


@pytest.mark.django_db
def test_one_to_one_relationship():
    """Test that each user can only have one pet"""
    user = User.objects.create_user(username="testuser", password="x")
    pet1 = DigitalPet.objects.create(user=user)

    # Trying to create another pet for same user should fail
    with pytest.raises(Exception):  # IntegrityError
        DigitalPet.objects.create(user=user)


@pytest.mark.django_db
def test_pet_deletion_on_user_deletion():
    """Test that pet is deleted when user is deleted (cascade)"""
    user = User.objects.create_user(username="testuser", password="x")
    pet = DigitalPet.objects.create(user=user)
    pet_id = pet.id

    # Delete user
    user.delete()

    # Pet should be deleted too
    assert not DigitalPet.objects.filter(id=pet_id).exists()


@pytest.mark.django_db
def test_stage_choices():
    """Test that all stage choices are valid"""
    stages = [choice[0] for choice in DigitalPet.STAGES]

    assert 'spark' in stages
    assert 'flicker' in stages
    assert 'flame' in stages
    assert 'blaze' in stages
    assert 'nova' in stages
    assert len(stages) == 5
