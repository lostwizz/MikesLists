import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_todo_list_view_renders(client):
    """
    Ensures the todo_list view renders the correct template.
    Covers the missing return line in the view.
    """
    # Create and log in a user
    user = User.objects.create_user(username="bob", password="x")
    client.login(username="bob", password="x")

    url = reverse("todo:list")
    response = client.get(url)

    assert response.status_code == 200
    assert "app_ToDo/todo_list.html" in [t.name for t in response.templates]
