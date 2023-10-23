def test_login_success(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Target Location' in response.data

def test_login_wrong_password(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$$"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Incorrect email or password' in response.data

def test_login_wrong_email(client):
    response = client.post('/login', data={
        "email": "testtest.com",
        "password": "123456789aA$"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Incorrect email or password' in response.data