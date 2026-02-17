# Pet System - Installation Steps

## 1. Replace model
cp pet_models.py /srv/django/MikesLists_dev/app_pet/models.py

## 2. Add signals file
cp pet_signals.py /srv/django/MikesLists_dev/app_pet/signals.py

## 3. Replace views
cp pet_views.py /srv/django/MikesLists_dev/app_pet/views.py

## 4. Replace URLs
cp pet_urls.py /srv/django/MikesLists_dev/app_pet/urls.py

## 5. Replace apps.py (wires signals in)
cp pet_apps.py /srv/django/MikesLists_dev/app_pet/apps.py

## 6. Replace template
cp pet_dashboard.html /srv/django/MikesLists_dev/app_pet/templates/app_pet/dashboard.html

## 7. Make and run migrations
cd /srv/django/MikesLists_dev
python manage.py makemigrations app_pet
python manage.py migrate

## 8. Restart service
sudo systemctl restart mikeslists-dev.service

## 9. Verify
python manage.py show_urls | grep pet
# Should show:
# /pet/              pet:dashboard
# /pet/sync-github/  pet:sync_github
# /pet/run-coverage/ pet:run_coverage

## New fields added to DigitalPet:
# - mood          (happy/content/tired/sad/starving)
# - hunger        (0-100)
# - xp            (total XP points)
# - commit_streak (consecutive commit days)
# - login_streak  (consecutive login days)
# - last_commit_date
# - last_login_date
# - coverage_score (last known %)

## XP Sources:
# - GitHub commit:    +10 per commit
# - Login streak day: +5
# - Admin action:     +3
# - Coverage >= 80%:  +20
# - Coverage >= 95%:  +50
# - 7-day streak:    +100 bonus
# - 30-day streak:   +500 bonus

## Daily Tick (hunger drain + mood update + de-evolution check)
# Runs lazily when dashboard is loaded (checks if updated_at < today)
# Or wire to cron:
# 0 0 * * * cd /srv/django/MikesLists_dev && python manage.py shell -c \
#   "from app_pet.models import DigitalPet; [p.daily_tick() for p in DigitalPet.objects.all()]"
