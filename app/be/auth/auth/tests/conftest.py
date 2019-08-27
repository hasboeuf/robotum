import pytest
import connexion
from connexion.resolver import RestyResolver

from auth.database import init_db
from auth.models import User

DEFAULT_USER = "user"
DEFAULT_PASSWORD = "pass"


@pytest.fixture(scope="session")
def client():
    app = connexion.FlaskApp(__name__)
    app.add_api("../definitions/api.yaml", resolver=RestyResolver(".."))
    flask_app = app.app
    flask_app.config["DATABASE_URI"] = "sqlite:///:memory:"

    init_db(app.app)

    flask_app.config["DEBUG"] = True
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def create_user(username=DEFAULT_USER, password=DEFAULT_PASSWORD, admin=True):
    user = User(username, password, admin)
    user.add()
    yield
    user.delete()
