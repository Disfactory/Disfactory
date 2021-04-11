def test_create_user(django_user_model):
    # fmt: off
    user = django_user_model.objects.create_user(
        username="thehyyu",
        email="backend@email.com",
        password="backend123",
    )
    # fmt: on
    assert user.username == "thehyyu"
    assert user.email == "backend@email.com"
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


def test_create_superuser(django_user_model):
    # fmt: off
    admin_user = django_user_model.objects.create_superuser(
        username="superadmin",
        email="superadmin@email.com",
        password="testpass123",
    )
    # fmt: on
    assert admin_user.username == "superadmin"
    assert admin_user.email == "superadmin@email.com"
    assert admin_user.is_active
    assert admin_user.is_staff
    assert admin_user.is_superuser
