"""Config edge cases: missing env vars, type coercion, defaults."""
import os
import pytest

from app.config import Config, ConfigError


REQUIRED = ["AWS_REGION", "BEDROCK_KB_ID", "BEDROCK_MODEL_ARN", "FLASK_SECRET_KEY"]


@pytest.fixture
def env(monkeypatch):
    for key in REQUIRED + ["BEDROCK_NUM_RESULTS", "FLASK_ENV"]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("BEDROCK_KB_ID", "kb-1")
    monkeypatch.setenv("BEDROCK_MODEL_ARN", "arn:aws:bedrock:::foundation-model/x")
    monkeypatch.setenv("FLASK_SECRET_KEY", "secret")
    return monkeypatch


def test_loads_when_all_required_present(env):
    cfg = Config.from_env()
    assert cfg.AWS_REGION == "us-east-1"
    assert cfg.BEDROCK_NUM_RESULTS == 5  # default
    assert cfg.FLASK_ENV == "production"  # default


def test_num_results_overridable(env):
    env.setenv("BEDROCK_NUM_RESULTS", "10")
    assert Config.from_env().BEDROCK_NUM_RESULTS == 10


@pytest.mark.parametrize("var", REQUIRED)
def test_missing_required_var_raises_configerror(env, var):
    env.delenv(var)
    with pytest.raises(ConfigError) as exc:
        Config.from_env()
    assert var in str(exc.value)


def test_blank_required_var_raises_configerror(env):
    env.setenv("BEDROCK_KB_ID", "   ")
    with pytest.raises(ConfigError):
        Config.from_env()


def test_num_results_invalid_raises(env):
    env.setenv("BEDROCK_NUM_RESULTS", "not-a-number")
    with pytest.raises(ValueError):
        Config.from_env()
