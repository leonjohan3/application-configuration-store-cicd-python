# conftest.py
# general-purpose fixtures
import pytest


@pytest.fixture(autouse=True)
def my_future_fixture_placeholder(monkeypatch):
    pass
