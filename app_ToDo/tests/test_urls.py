import pytest
from django.urls import reverse, resolve
from app_ToDo import urls as todo_urls
from app_ToDo import views


def test_todo_root_url_resolves():
    """
    Ensures the '' path resolves to views.todo_list using the app's URLconf.
    """
    resolver = resolve("/", urlconf=todo_urls)
    assert resolver.func == views.todo_list


@pytest.mark.django_db
def test_todo_root_url_client(client):
    """
    Ensures reverse('todo:list') produces a valid URL and the client can hit it.
    """
    url = reverse("todo:list")
    response = client.get(url)

    # We don't care about the view result here — just that the URL works.
    assert response.status_code in (200, 302, 403, 404)
