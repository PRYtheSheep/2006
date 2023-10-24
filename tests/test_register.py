def test_register_email_taken(client):
    response = client.post('/register', data={
        "first_name": "Test",
        "last_name": "User",
        "email": "test@test.com",
        "password": "123456789aA$",
        "confirm_password": "123456789aA$",
        "register_as": "tenant"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Email: Email is already taken' in response.data

def test_register_email_invalid(client):
    response = client.post('/register', data={
        "first_name": "Test",
        "last_name": "User",
        "email": "testtest.com",
        "password": "123456789aA$",
        "confirm_password": "123456789aA$",
        "register_as": "tenant"
    }, follow_redirects=True)
    print(response.data)
    assert response.status_code == 200
    assert b'Invalid email address.' in response.data

def test_register_password_not_match(client):
    response = client.post('/register', data={
        "first_name": "Test",
        "last_name": "User",
        "email": "new_user@test.com",
        "password": "123456789aA$",
        "confirm_password": "123456789aA$$",
        "register_as": "tenant"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Passwords must match.' in response.data

def test_register_password_not_strong(client):
    response = client.post('/register', data={
        "first_name": "Test",
        "last_name": "User",
        "email": "new_user@test.com",
        "password": "123456789",
        "confirm_password": "123456789",
        "register_as": "tenant"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'The password must be 12-18 characters, contain at least one letter, one number and one special character.' in response.data

def test_register_password_not_strong2(client):
    response = client.post('/register', data={
        "first_name": "Test",
        "last_name": "User",
        "email": "new_user@test.com",
        "password": "123456789aA",
        "confirm_password": "123456789aA",
        "register_as": "tenant"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'The password must be 12-18 characters, contain at least one letter, one number and one special character.' in response.data

# need to delete user from database after this test
# def test_register_success(client):
#     response = client.post('/register', data={
#         "first_name": "Test",
#         "last_name": "User",
#         "email": "new_user@email.com",
#         "password": "123456789aA$",
#         "confirm_password": "123456789aA$",
#         "register_as": "tenant"
#     }, follow_redirects=True)

#     assert response.status_code == 200
#     assert b'Registered Successfully' in response.data
