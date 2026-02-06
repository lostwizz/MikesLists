import pytest
from django.test import override_settings
from app_core.utils.env import get_env, is_dev
from app_core.services.health_service import CheckResult

@pytest.mark.django_db
class TestBaseLogic:

    @override_settings(ENV_NAME="dev")
    def test_dev_masking_disabled(self):
        """Ensure raw_data is visible in DEV."""
        res = CheckResult(name="cpu", status="ok", message="low", raw_value="0.1")
        data = res.to_dict()
        print(f"{data=} {get_env()} {is_dev()=}")
        assert "raw_value" in data
        assert data["raw_value"] == "0.1"

        assert "message" in data
        assert data["message"] == "low"

    @override_settings(ENV_NAME="live")
    def test_live_masking_enabled(self):
        """Ensure sensitive fields are GONE in LIVE."""
        res = CheckResult(name="cpu", status="ok", message="low", raw_value="0.1")
        data = res.to_dict()
        assert "raw_value" not in data
        assert "message" not in data

    @override_settings(ENV_NAME="live")
    def test_env_string_returned(self):
        """Verify get_env returns a string, not an Enum (prevents JSON errors)."""
        assert get_env() == "live"
        assert isinstance(get_env(), str)


@pytest.mark.django_db
class TestEnvironmentEdgeCases:

    @override_settings(ENV_NAME="  DEV  ")  # Test case sensitivity and whitespace
    def test_whitespace_and_case_tolerance(self):
        """Ensure the helper handles non-standard casing and whitespace."""
        assert get_env() == "dev"
        assert is_dev() is True

    @override_settings(ENV_NAME="production") # Test unknown strings
    def test_unknown_env_fallback(self):
        """Ensure unknown environments fallback safely to DEV (or your chosen default)."""
        # Based on your current logic, it falls back to DEV
        assert get_env() == "dev"
        assert is_dev() is True
