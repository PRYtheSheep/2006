import pytest

from main.website import create_app, register

@pytest.fixture()
def app():
    app = create_app()
    app = register(app)
    app.config['WTF_CSRF_ENABLED'] = False

    yield app
        
@pytest.fixture()
def client(app):
    return app.test_client()