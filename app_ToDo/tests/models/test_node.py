import pytest
from django.contrib.auth.models import User, Group
from app_ToDo.models.node import Node


@pytest.mark.django_db
def test_node_str():
    user = User.objects.create(username="bob")
    group = Group.objects.create(name="testgroup")

    node = Node.objects.create(
        name="My Node",
        short_name="node",
        user_obj=user,
    )
    node.visibility_allowed_groups.add(group)

    assert str(node) == "My Node"
