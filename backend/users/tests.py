from django.contrib.auth import get_user_model
from django.test import TestCase


class CustomUserTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        # fmt: off
        user = User.objects.create_user(
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

    def test_create_superuser(self):
        User = get_user_model()
        # fmt: off
        admin_user = User.objects.create_superuser(
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
