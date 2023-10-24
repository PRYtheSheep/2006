def test_account_settings_not_logged_in(client):
    response = client.get('/settings', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Please login to access this page.' in response.data

def test_account_settings_logged_in(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)
    response = client.get('/settings', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Account Settings' in response.data

def test_change_username(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)
    response = client.post('/settings/account', data={
        "username": "test_user",
        "password": "123456789aA$"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Account Information Changed Successfully' in response.data

def test_change_username_failed(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)
    response = client.post('/settings/account', data={
        "username": "test_user",
        "password": "123456789aA"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Password entered is wrong' in response.data

def test_change_password(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)
    response = client.post('/settings/password', data={
        "current_password": "123456789aA$",
        "new_password": "123456789aA$",
        "confirm_new_password": "123456789aA$"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your password is successfully updated.' in response.data

def test_change_password_wrong_current_password(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)

    response = client.post('/settings/password', data={
        "current_password": "123456789aA",
        "new_password": "123456789aA$",
        "confirm_new_password": "123456789aA$"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Current Password is wrong' in response.data

def test_change_password_wrong_confirm_password(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)

    response = client.post('/settings/password', data={
        "current_password": "123456789aA$",
        "new_password": "123456789aA$",
        "confirm_new_password": "123456789aA"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Passwords must match' in response.data

def test_change_password_wrong_new_password(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)

    response = client.post('/settings/password', data={
        "current_password": "123456789aA$",
        "new_password": "123456789aA",
        "confirm_new_password": "123456789aA"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'The password must be 12-18 characters, contain at least one letter, one number and one special character' in response.data

