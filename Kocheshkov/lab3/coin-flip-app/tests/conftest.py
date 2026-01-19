# tests/conftest.py
import pytest
from tests.config import create_driver

@pytest.fixture
def driver():
    d = create_driver()
    yield d
    d.quit()
