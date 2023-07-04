import os
import pytest


# important: this line needs to be set BEFORE the "app" import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
from main import app, db


@pytest.fixture
def client():
    client = app.test_client()
    cleanup()  # clean up before every test
    db.create_all()
    yield client


def cleanup():
    # clean up/delete the DB (drop all tables in the database)
    db.drop_all()


def test_secret_number_page_exists(client):
    response = client.get("/")
    assert b'Guess the secret number' in response.data
