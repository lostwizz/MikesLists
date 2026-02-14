"""
app_accounts.tests.test_urls
/srv/django/MikesLists_dev/app_accounts/tests/test_urls.py

"""
# from django.test import TestCase
import pytest



@pytest.mark.django_db
def test_logged_out_renders_template_client(client):
    from django.urls import reverse

    response = client.get(reverse("accounts:logged_out"))

    assert response.status_code == 200
    assert "registration/logged_out.html" in [t.name for t in response.templates]




@pytest.mark.django_db
def test_logout_allow_get_calls_post(mocker):
    from django.test import RequestFactory
    from app_accounts.urls import LogoutAllowGet

    rf = RequestFactory()
    request = rf.get("/accounts/logout/")

    view = LogoutAllowGet()
    mock_post = mocker.patch.object(view, "post", return_value="POST_CALLED")

    result = view.get(request)

    assert result == "POST_CALLED"
    mock_post.assert_called_once()


@pytest.mark.django_db
def test_logged_out_renders_template_client(client):
    from django.urls import reverse

    response = client.get(reverse("accounts:logged_out"))

    assert response.status_code == 200
    assert "registration/logged_out.html" in [t.name for t in response.templates]
