from django.urls import path
from . import views

app_name = "pet"

urlpatterns = [
    path("", views.pet_dashboard, name="dashboard"),
    path("sync-github/", views.fetch_github_commits, name="sync_github"),
    path("run-coverage/", views.run_coverage, name="run_coverage"),
]
